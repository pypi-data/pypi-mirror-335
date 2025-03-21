"""
The Distributed Dictionary is a performant and distributed key-value store
that is available to applications and workflows written for the Dragon ecosystem.

This is Dragon's specialized implementation based on the Dragon file-like interface
which relies on Dragon Channels. The Distributed Dictionary is to work like a standard
Python dictionary except that the data that it holds may span multiple nodes and be
larger than any one node can hold.

The manager manages on shard of a distributed database. Selection of the manager is based
on the hashed value of the key being used for the insertion of key/value pairs within
the distributed dictionary.

"""

import os
import logging
import traceback
import socket
import os
import cloudpickle

from ...utils import b64decode, b64encode, set_local_kv, host_id, B64
from ... import managed_memory as dmem
from ...globalservices import channel
from ...globalservices import pool
from ...infrastructure import facts
from ...infrastructure import parameters
from ...infrastructure import util as dutil
from ...infrastructure import messages as dmsg
from ...infrastructure.channel_desc import ChannelOptions
from ...localservices.options import ChannelOptions as LSChannelOptions
from ...channels import Channel
from ... import fli
from ...rc import DragonError
from .ddict import KEY_HINT, VALUE_HINT, DDictManagerFull, DDictCheckpointSync, DDictManagerStats
from ...dlogging.util import setup_BE_logging, DragonLoggingServices as dls

log = None
MAX_NUM_CLIENTS_PER_MANAGER = 100000

# These are client-side streams used only in communicating to other
# managers for a few primitives when forwarding is needed.
NUM_STREAMS_PER_MANAGER = 3

# This is used to make it possible to still use the managed memory pool
# when it is getting fully utilized to be able to respond to requests
# by rejecting additional puts.
RESERVED_POOL_SPACE = 1024**2


def id_set(aSet):
    ret_val = set()
    for item in aSet:
        ret_val.add(item.id)

    return ret_val


def mem_set(aSet, pool, reattach):
    if not reattach:
        return aSet

    ret_val = set()
    for key in aSet:
        ret_val.add(pool.alloc_from_id(key))

    return ret_val


def map_to_ids(aDict):
    ret_val = dict()
    for key in aDict:
        mem_lst = aDict[key]
        int_lst = []
        for item in mem_lst:
            int_lst.append(item.id)
        ret_val[key.id] = int_lst

    return ret_val


def key_allocs_to_ids(aDict):
    ret_val = dict()
    for key in aDict:
        ret_val[key.id] = aDict[key].id

    return ret_val


def key_allocs_from_ids(aDict, pool, reattach):
    if not reattach:
        return aDict

    ret_val = dict()
    for key in aDict:
        ret_val[pool.alloc_from_id(key)] = pool.alloc_from_id(aDict[key])

    return ret_val


def map_from_ids(aDict, pool, reattach):
    if not reattach:
        return aDict

    ret_val = dict()
    for key in aDict:
        int_lst = aDict[key]
        mem_lst = []
        for item in int_lst:
            mem_lst.append(pool.alloc_from_id(item))
        ret_val[pool.alloc_from_id(key)] = mem_lst

    return ret_val


class Checkpoint:
    """
    Key_allocs maps keys to their memory allocation within the dictionary's pool.
    This is necessary to have a reference to these pool allocations so they
    can be managed. The map field maps keys to their values within the
    dictionary's pool. Values are always a list of pool allocations. The
    deleted set is the set of persistent keys that are deleted in this
    checkpoint, thereby masking any persistent keys that exist in earlier
    checkpoints. The persist set is the set of any keys that should persist
    going forward when "wait for keys" is specified. If "wait for keys" is
    not specified, then all keys persist and this set is not used. The id is
    the checkpoint id of the checkpoint which does not change for a
    checkpoint but monontonically increases for all checkpoints.
    """

    def __init__(self, id: int, move_to_pool: object, manager: object):
        self.id = id
        self.move_to_pool = move_to_pool
        self.key_allocs = dict()
        self.map = dict()
        self.deleted = set()
        self.persist = set()
        self.writers = set()
        self.manager = manager

    def __setstate__(self, args):
        (self.id, key_allocs, map, deleted, persist, self.writers, thePool, reattach) = args
        self.key_allocs = key_allocs_from_ids(key_allocs, thePool, reattach)
        self.map = map_from_ids(map, thePool, reattach)
        self.deleted = mem_set(deleted, thePool, reattach)
        self.persist = mem_set(persist, thePool, reattach)

        self._move_to_pool = None

    def __getstate__(self):
        # Do not pickle move_to_pool as it is a manager function. If pickle the function, the
        # pickle structure is cyclic, leading to system stack overflow.
        return (
            self.id,
            key_allocs_to_ids(self.key_allocs),
            map_to_ids(self.map),
            id_set(self.deleted),
            id_set(self.persist),
            self.writers,
            self.manager._pool,
            self.manager._reattach,
        )

    def build_allocs(self, allocs: dict):
        for key_mem in self.key_allocs.keys():
            allocs[key_mem.id] = key_mem

        for val_mems in self.map.values():
            # value is a list of memory allocations
            for val_mem in val_mems:
                allocs[val_mem.id] = val_mem

    def redirect(self, indirect: dict):
        # redirect all map/set (map, key_allocs, deleted, persist)
        new_map = dict()
        for key, values in self.map.items():
            val_list = []
            for val in values:
                val_list.append(indirect[val])
            new_map[indirect[key]] = val_list
        self.map = new_map

        new_key_allocs = dict()
        for key, val in self.key_allocs.items():
            new_key_allocs[indirect[key]] = indirect[val]
        self.key_allocs = new_key_allocs

        new_deleted = set()
        for mem_id in self.deleted:
            new_deleted.add(indirect[mem_id])
        self.deleted = new_deleted

        new_persist = set()
        for mem_id in self.persist:
            new_persist.add(indirect[mem_id])
        self.persist = new_persist

    def set_manager(self, manager):
        self.manager = manager

    def set_pool_mover(self, move_to_pool):
        self.move_to_pool = move_to_pool

    def _contains(self, msg_key_mem):
        if msg_key_mem in self.map:
            ec = DragonError.SUCCESS
            key_mem = self.key_allocs[msg_key_mem]
        else:
            key_mem = None
            ec = DragonError.KEY_NOT_FOUND

        return ec, key_mem

    def _contains_and_free_msg_key(self, msg_key_mem):
        ec, key_mem = self._contains(msg_key_mem)

        # We must free the messages key memory
        self.manager.check_for_key_existence_before_free(msg_key_mem)

        return ec, key_mem

    def contains_put_key(self, client_key_mem):
        if client_key_mem in self.map:
            key_mem = self.key_allocs[client_key_mem]
            self.manager.check_for_key_existence_before_free(client_key_mem)
            ec = DragonError.SUCCESS
        else:
            key_mem = self.move_to_pool(client_key_mem)
            self.key_allocs[key_mem] = key_mem
            ec = DragonError.KEY_NOT_FOUND

        return ec, key_mem

    def clear(self):
        keys = set(self.map.keys())

        while len(keys) > 0:
            key = keys.pop()
            values = self.map[key]
            while len(values) > 0:
                val_mem = values.pop()
                val_mem.free()
            key_mem = self.key_allocs[key]
            # See retire checkpoint code for
            # why these dels are here.
            del self.map[key]
            del self.key_allocs[key]
            key_mem.free()
        self.map.clear()
        self.persist.clear()
        self.deleted.clear()
        self.writers.clear()


class DictOp:
    """
    Base class for all deferred operations. Client id, checkpoint id, message tag
    are common to all dictionary operations.
    """

    def __init__(self, manager: object, client_id: int, chkpt_id: int, tag: int):
        self.manager = manager
        self.client_id = client_id
        self.chkpt_id = chkpt_id
        self.tag = tag

    def __str__(self):
        return f"{self.__class__.__name__}{self.client_id, self.chkpt_id, self.tag}"

    def perform(self) -> bool:
        """
        Returns True when it was performed and false otherwise.
        """
        raise ValueError("Cannot perform the base class Dictionary Operator. Undefined.")


class PutOp(DictOp):

    def __init__(
        self,
        manager: object,
        client_id: int,
        chkpt_id: int,
        tag: int,
        persist: bool,
        client_key_mem: object,
        val_list: list,
    ):
        super().__init__(manager, client_id, chkpt_id, tag)
        self.persist = persist
        self.client_key_mem = client_key_mem
        self.val_list = val_list

    def perform(self) -> bool:
        """
        Returns True when it was performed and false otherwise.
        """
        chkpt = self.manager._working_set.put(self.chkpt_id)

        if chkpt is None:
            self.manager._traceit("Deferring put operation because checkpoint is not available yet.")
            return False

        ec, key_mem = chkpt.contains_put_key(self.client_key_mem)
        # the underlying memory in the pool needs to be cleaned up if we put the same key-value pair into the dictionary
        if ec == DragonError.SUCCESS:
            old_vals = chkpt.map[key_mem]  # free old value memory
            chkpt.map[key_mem] = []  # just in case of error while freeing
            while len(old_vals) > 0:
                try:
                    val = old_vals.pop()
                    val.free()
                except Exception as ex:
                    log.info("There was an error while freeing value being replaced. %s", ex)

        chkpt.map[key_mem] = self.val_list
        if self.persist:
            chkpt.persist.add(key_mem)
        if key_mem in chkpt.deleted:  # if non-persistent key is the same as a deleted persistent key
            chkpt.deleted.remove(key_mem)

        chkpt.writers.add(self.client_id)

        resp_msg = dmsg.DDPutResponse(self.manager._tag_inc(), ref=self.tag, err=DragonError.SUCCESS)
        self.manager._send_msg(resp_msg, self.manager._buffered_client_connections_map[self.client_id])
        return True


class GetOp(DictOp):

    def __init__(self, manager: object, client_id: int, chkpt_id: int, tag: int, client_key_mem: object):
        super().__init__(manager, client_id, chkpt_id, tag)
        self.client_key_mem = client_key_mem

    def perform(self) -> bool:
        """
        Returns True when it was performed and false otherwise.
        """
        chkpt = self.manager._working_set.get(self.client_key_mem, self.chkpt_id)

        if chkpt is None:
            # We are waiting for keys or for some other reason
            # cannot perform this yet.
            return False

        ec, key_mem = chkpt._contains_and_free_msg_key(self.client_key_mem)

        resp_msg = dmsg.DDGetResponse(self.manager._tag_inc(), ref=self.tag, err=ec)
        self.manager._send_dmsg_and_value(
            chkpt=chkpt,
            resp_msg=resp_msg,
            connection=self.manager._client_connections_map[self.client_id],
            key_mem=key_mem,
            transfer_ownership=False,
        )

        self.manager._working_set.update_writer_checkpoint(self.client_id, self.chkpt_id)

        return True


class PopOp(DictOp):

    def __init__(self, manager: object, client_id: int, chkpt_id: int, tag: int, client_key_mem: object):
        super().__init__(manager, client_id, chkpt_id, tag)
        self.client_key_mem = client_key_mem

    def perform(self) -> bool:
        """
        Returns True when it was performed and false otherwise.
        """
        chkpt = self.manager._working_set.get(self.client_key_mem, self.chkpt_id)

        if chkpt is None:
            # We are waiting for keys or for some other reason
            # cannot perform this yet.
            return False

        ec, key_mem = chkpt._contains(self.client_key_mem)

        transfer_ownership = True

        if ec == DragonError.SUCCESS:

            if self.chkpt_id > self.manager._working_set.newest_chkpt_id:
                # It was a pop on a newer checkpoint and the key exists but
                # we are not ready to pop it yet.
                return False

            current_chkpt = self.manager._working_set.access(self.chkpt_id)
            current_chkpt.writers.add(self.client_id)

            if chkpt.id < self.chkpt_id:
                # if the key was found in an earlier checkpoint, it cannot be removed.
                current_chkpt.deleted.add(key_mem)
                current_chkpt.key_allocs[key_mem] = key_mem
                transfer_ownership = False

            # Otherwise it was found in the current checkpoint and we should transfer ownership
            # when we send it.

        # Now free the client message memory for the key since we are done.
        self.manager.check_for_key_existence_before_free(self.client_key_mem)

        resp_msg = dmsg.DDPopResponse(self.manager._tag_inc(), ref=self.tag, err=ec)
        self.manager._send_dmsg_and_value(
            chkpt=chkpt,
            resp_msg=resp_msg,
            connection=self.manager._client_connections_map[self.client_id],
            key_mem=key_mem,
            transfer_ownership=transfer_ownership,
        )

        return True


class ContainsOp(DictOp):

    def __init__(self, manager: object, client_id: int, chkpt_id: int, tag: int, client_key_mem: object):
        super().__init__(manager, client_id, chkpt_id, tag)
        self.client_key_mem = client_key_mem

    def perform(self) -> bool:
        """
        Returns True when it was performed and false otherwise.
        Defer the operation if a non-persistent key hasn't been added to the checkpoint.
        """
        # if request a future checkpoint that hasn't existed in current working set,
        # we look into all checkpoints in current working set
        newest_chkpt_id_chkpt = self.manager._working_set.newest_chkpt_id
        if self.chkpt_id > newest_chkpt_id_chkpt:
            chkpt = self.manager._working_set.get(self.client_key_mem, newest_chkpt_id_chkpt)
        else:
            chkpt = self.manager._working_set.get(self.client_key_mem, self.chkpt_id)

        if chkpt is None:
            # We don't wait in contains operation
            ec = DragonError.KEY_NOT_FOUND
            self.manager.check_for_key_existence_before_free(self.client_key_mem)

        else:
            ec, key_mem = chkpt._contains_and_free_msg_key(self.client_key_mem)
            # a future checkpoint shouldn't return a nonpersistent key in newest chekcpoint
            if self.chkpt_id > newest_chkpt_id_chkpt and key_mem not in chkpt.persist:
                ec = DragonError.KEY_NOT_FOUND

        resp_msg = dmsg.DDContainsResponse(self.manager._tag_inc(), ref=self.tag, err=ec)
        self.manager._send_msg(resp_msg, self.manager._buffered_client_connections_map[self.client_id])

        self.manager._working_set.update_writer_checkpoint(self.client_id, self.chkpt_id)

        return True


class LengthOp(DictOp):

    def __init__(self, manager: object, client_id: int, chkpt_id: int, tag: int, respFLI: str):
        super().__init__(manager, client_id, chkpt_id, tag)
        self.respFLI = respFLI

    def perform(self) -> bool:
        """
        Returns True when it was performed and false otherwise.
        """
        keys = self.manager._working_set.keys(self.chkpt_id)

        resp_msg = dmsg.DDLengthResponse(
            self.manager._tag_inc(), ref=self.tag, err=DragonError.SUCCESS, length=len(keys)
        )
        connection = fli.FLInterface.attach(b64decode(self.respFLI))
        self.manager._send_msg(resp_msg, connection)
        connection.detach()

        self.manager._working_set.update_writer_checkpoint(self.client_id, self.chkpt_id)

        return True


class KeysOp(DictOp):

    def __init__(self, manager: object, client_id: int, chkpt_id: int, tag: int):
        super().__init__(manager, client_id, chkpt_id, tag)

    def perform(self) -> bool:
        """
        Returns True when it was performed and false otherwise.
        """
        keys = self.manager._working_set.keys(self.chkpt_id)

        resp_msg = dmsg.DDKeysResponse(self.manager._tag_inc(), ref=self.tag, err=DragonError.SUCCESS)

        self.manager._send_dmsg_and_keys(resp_msg, self.manager._client_connections_map[self.client_id], keys)

        self.manager._working_set.update_writer_checkpoint(self.client_id, self.chkpt_id)

        return True


class ClearOp(DictOp):

    def __init__(self, manager: object, client_id: int, chkpt_id: int, tag: int, respFLI: str):
        super().__init__(manager, client_id, chkpt_id, tag)
        self.respFLI = respFLI

    def perform(self) -> bool:
        """
        Returns True when it was performed and false otherwise.
        """

        ckpt = self.manager._working_set.access(self.chkpt_id)
        if ckpt is None:
            return False

        ckpt.clear()

        resp_msg = dmsg.DDClearResponse(self.manager._tag_inc(), ref=self.tag, err=DragonError.SUCCESS)
        connection = fli.FLInterface.attach(b64decode(self.respFLI))
        self.manager._send_msg(resp_msg, connection)
        connection.detach()

        self.manager._working_set.update_writer_checkpoint(self.client_id, self.chkpt_id)

        return True


class WorkingSet:
    def __init__(
        self, *, manager, move_to_pool, deferred_ops, working_set_size, wait_for_keys, wait_for_writers, start=0
    ):
        self._manager = manager
        self._move_to_pool = move_to_pool  # This is a function from the manager.
        self._deferred_ops = deferred_ops
        self._working_set_size = working_set_size
        self._wait_for_keys = wait_for_keys
        self._wait_for_writers = wait_for_writers
        self._chkpts = {}

        for i in range(start, start + working_set_size):
            self._chkpts[i] = Checkpoint(id=i, move_to_pool=move_to_pool, manager=self._manager)

        self._next_id = start + working_set_size

    def __setstate__(self, args):
        (self._working_set_size, self._wait_for_keys, self._wait_for_writers, self._chkpts, self._next_id) = args
        self._deferred_ops = {}

    def __getstate__(self):
        # Do not pickle move_to_pool as it is a manager function. If pickle the function, the
        # pickle structure is cyclic, leading to system stack overflow.
        return (self._working_set_size, self._wait_for_keys, self._wait_for_writers, self._chkpts, self._next_id)

    def build_allocs(self):
        allocs = dict()
        for chkpt_id in self._chkpts:
            self._chkpts[chkpt_id].build_allocs(allocs)
        return allocs

    def redirect(self, indirect: dict):
        for chkpt_id in self._chkpts:
            self._chkpts[chkpt_id].redirect(indirect)

    def set_manager(self, manager):
        self._manager = manager
        for chkpt_id in self._chkpts:
            chkpt = self._chkpts[chkpt_id]
            chkpt.set_manager(manager)

    def check_for_key_existence_before_free(self, key):
        found_in_working_set = False
        for chkpt_id in self._chkpts:
            chkpt = self._chkpts[chkpt_id]
            if key in chkpt.map:
                other_key = chkpt.key_allocs[key]
                if key.is_the_same_as(other_key):
                    found_in_working_set = True
                    tb = traceback.format_stack()
                    log.debug("Asked to free memory that is still in use. Traceback:%s", tb)
                    # Comment out line below to keep running in presence of this error.
                    raise Exception(f"Key is to be freed, but exists in checkpoint {chkpt.id}")

        if not found_in_working_set:
            key.free()

    def _retire_checkpoint(self, parent, child):
        kvs_to_free = set()
        for key in parent.map:
            copied = False
            if key not in child.map and key not in child.deleted:
                # This key must be persistent or we wouldn't be retiring this checkpoint
                # so it should be copied. But also add it to persist if wait for keys.
                if self._wait_for_keys:
                    child.persist.add(key)
                child.map[key] = parent.map[key]
                child.key_allocs[key] = parent.key_allocs[key]
                copied = True

            if not copied:
                kvs_to_free.add(key)

        while len(kvs_to_free) > 0:
            key = kvs_to_free.pop()
            values = parent.map[key]
            while len(values) > 0:
                val_mem = values.pop()
                val_mem.free()
            # We must del the key in the two maps
            # below because otherwise the dictionary
            # implementation, looking for another key
            # that maps to the same position in the
            # map or key_allocs dictionaries, would get
            # an error while probing because this key's
            # memory would be freed and could not
            # be compared for equality. This was seen
            # in some demo code so it is known that this
            # would be a problem without the code written
            # as it is here even though we clear the maps
            # just below.
            del parent.map[key]
            key_mem = parent.key_allocs[key]
            del parent.key_allocs[key]
            key_mem.free()

        parent.key_allocs.clear()
        parent.map.clear()
        parent.deleted.clear()
        parent.writers.clear()
        child.deleted.clear()

        del self._chkpts[parent.id]

    @property
    def range(self):
        return (min(self._chkpts), max(self._chkpts))

    @property
    def newest_chkpt_id(self):
        return max(self._chkpts)

    @property
    def oldest_chkpt_id(self):
        return max(0, self._next_id - self._working_set_size)

    def advance(self) -> bool:
        # advance and return True if we could advance and False otherwise.
        if len(self._chkpts) == self._working_set_size:
            id_to_retire = self._next_id - self._working_set_size
            parent = self._chkpts[id_to_retire]
            child = self._chkpts[id_to_retire + 1]
            # We need to retire a Checkpoint
            if self._wait_for_keys:
                parent_non_persist_keys = parent.map.keys() - parent.persist
                child_non_persist_keys = child.map.keys() - child.persist - parent.persist

                if len(parent_non_persist_keys - child_non_persist_keys) != 0:
                    # We must wait for more non persisting keys
                    # in the next to last oldest checkpoint.
                    return False

            if self._wait_for_writers:
                if len(parent.writers - child.writers) != 0:
                    # superset may not be accurate since children could have more
                    # writers than a parent and that would be OK. Subtracting child
                    # from parent will be less error-prone.
                    return False

            self._retire_checkpoint(parent, child)

        self._chkpts[self._next_id] = Checkpoint(
            id=self._next_id, move_to_pool=self._move_to_pool, manager=self._manager
        )
        self._next_id += 1
        return True

    def get(self, key, chkpt_id: int) -> Checkpoint:
        """
        Return the checkpoint for the key of a checkpoint. If it
        is not yet a valid checkpoint and we have deferred ops,
        or need to wait, then return None.
        """
        newest_chkpt_id = self.newest_chkpt_id
        oldest_chkpt_id = self.oldest_chkpt_id

        # Asking for a retired checkpoint that no longer exist.
        if chkpt_id < oldest_chkpt_id:
            raise DDictCheckpointSync(
                DragonError.DDICT_CHECKPOINT_RETIRED,
                f"The checkpoint id {chkpt_id} is older than the working set and cannot be used for a get operation.",
            )

        if chkpt_id > newest_chkpt_id and key not in self._chkpts[oldest_chkpt_id].persist:
            # Then we are asking for a checkpoint that doesn't exist yet. Persistent
            # keys are read from older checkpoints as if they were current. Not so for
            # non-persistent keys.
            if (chkpt_id in self._deferred_ops) or self._wait_for_keys:
                # There are waiting put operations so wait with this get as well.
                return None

        chkpt_start = min(chkpt_id, newest_chkpt_id)
        for i in range(chkpt_start, oldest_chkpt_id - 1, -1):
            chkpt = self._chkpts[i]
            if key in chkpt.map:
                if self._wait_for_keys and key not in chkpt.persist and chkpt_id > chkpt.id:
                    # This is a non-persistent key, wait_for_keys was specified, and the client
                    # is beyond this checkpoint. So client should wait.
                    return None

                return chkpt

            if key in chkpt.deleted:
                return chkpt  # return Checkpoint even though not present. It will be looked up.

        # Not found, so return a checkpoint unless wait_for_keys is specified.
        if chkpt_id in self._chkpts:
            if self._wait_for_keys and key not in chkpt.map:
                return None
            return self._chkpts[chkpt_id]

        return self._chkpts[oldest_chkpt_id]  # Not found so return the oldest checkpoint

    def put(self, chkpt_id) -> Checkpoint:
        """
        Returns the checkpoint where the key/value pair should be
        put or None if the checkpoint is not yet available.
        """
        newest_chkpt_id = self.newest_chkpt_id
        oldest_chkpt_id = self.oldest_chkpt_id

        if chkpt_id < oldest_chkpt_id:
            raise DDictCheckpointSync(
                DragonError.DDICT_CHECKPOINT_RETIRED,
                f"The checkpoint id {chkpt_id} is older than the working set and cannot be used for a put operation.",
            )

        while chkpt_id > newest_chkpt_id and self.advance():
            newest_chkpt_id = min(self._next_id - 1, chkpt_id)

        if chkpt_id not in self._chkpts:
            return None

        return self._chkpts[chkpt_id]

    def keys(self, chkpt_id) -> Checkpoint:
        """
        Return the key set for a checkpoint. If it is not yet
        a valid checkpoint and we have deferred ops, or need
        to wait, then return None.
        """
        newest_chkpt_id = self.newest_chkpt_id
        oldest_chkpt_id = self.oldest_chkpt_id

        # Asking for a retired checkpoint that no longer exist.
        if chkpt_id < oldest_chkpt_id:
            raise DDictCheckpointSync(
                DragonError.DDICT_CHECKPOINT_RETIRED,
                f"The checkpoint id {chkpt_id} is older than the working set and cannot be used for a get operation.",
            )

        keys = set()
        # If the checkpoint does not yet exist, we add all
        # persistent keys in but leave out the non-persistent
        # ones (i.e. when wait for keys was specififed).
        chkpt_end = min(chkpt_id, newest_chkpt_id)
        for i in range(oldest_chkpt_id, chkpt_end + 1):
            current_chkpt = self._chkpts[i]
            keys = keys - current_chkpt.deleted
            if not self._wait_for_keys:
                keys = keys | current_chkpt.map.keys()
            else:
                keys = keys | current_chkpt.persist
        if chkpt_id in self._chkpts:
            keys = keys | self._chkpts[chkpt_id].map.keys()
        return keys

    def update_writer_checkpoint(self, client_id, chkpt_id):
        found = False
        current_id = min(chkpt_id, self.newest_chkpt_id)
        for i in range(self.oldest_chkpt_id, current_id):
            chkpt = self._chkpts[i]
            if client_id in chkpt.writers:
                found = True

        if found:
            for i in range(self.oldest_chkpt_id, current_id):
                chkpt = self._chkpts[i]
                chkpt.writers.add(client_id)

    def access(self, chkpt_id) -> Checkpoint:
        """
        Return the checkpoint object of a checkpoint id. If it
        is not yet a valid checkpoint and we have deferred ops,
        or need to wait, then return None.
        """
        oldest_chkpt_id = self.oldest_chkpt_id

        # Asking for a retired checkpoint that no longer exist.
        if chkpt_id < oldest_chkpt_id:
            raise DDictCheckpointSync(
                DragonError.DDICT_CHECKPOINT_RETIRED,
                f"The checkpoint id {chkpt_id} is older than the working set and cannot be used for a the operation.",
            )

        while chkpt_id not in self._chkpts and self.advance():
            pass

        if chkpt_id not in self._chkpts:
            return None

        return self._chkpts[chkpt_id]

    @property
    def key_count(self):
        """
        Return the total number of keys in the working set.
        """
        count = 0
        newest_chkpt_id = self.newest_chkpt_id
        oldest_chkpt_id = self.oldest_chkpt_id

        for i in range(oldest_chkpt_id, newest_chkpt_id + 1):
            current_chkpt = self._chkpts[i]
            count += len(current_chkpt.map)

        return count


class Manager:

    _DTBL = {}  # dispatch router, keyed by type of message

    def __init__(
        self, pool_size: int, serialized_return_orc, serialized_main_orc, trace, args, manager_id, ser_pool_desc
    ):
        (
            self._working_set_size,
            self._wait_for_keys,
            self._wait_for_writers,
            self._policy,
            self._persist_freq,
            self._name,
            self._timeout,
            self._restart,
        ) = args
        self._puid = parameters.this_process.my_puid
        self._trace = trace
        self._manager_id = manager_id
        self._tag = 0

        self.iterators = {}
        self._iter_id = 0
        self._abnormal_termination = False
        self._managers = []
        self._manager_hostnames = []
        self._serialized_manager_nodes = []
        self._manager_flis = {}
        self._serialized_main_orc = serialized_main_orc
        self._serialized_return_orc = serialized_return_orc

        self._host_id = host_id()
        self._serving = False
        self._allow_restart = False
        self._registered = False  # True if manager registers with orchestrator successfully
        self._reattach = True  # Used for dictionary synchronization

        err_str = ""
        err_code = DragonError.SUCCESS

        fname = f"{dls.DD}_{socket.gethostname()}_manager_{str(self._puid)}.log"
        global log
        if log == None:
            setup_BE_logging(service=dls.DD, fname=fname)
            log = logging.getLogger(str(dls.DD))

        try:
            log.debug("Starting manager on host = %s", socket.gethostname())

            # create manager's buffered_return_connector
            self._buffered_return_channel = Channel.make_process_local()
            self._buffered_return_connector = fli.FLInterface(
                main_ch=self._buffered_return_channel, use_buffered_protocol=True
            )
            self._serialized_buffered_return_connector = b64encode(self._buffered_return_connector.serialize())

            # create manager's return_connector
            self._return_channel = Channel.make_process_local()
            self._return_connector = fli.FLInterface(main_ch=self._return_channel)
            self._serialized_return_connector = b64encode(self._return_connector.serialize())

            # create a few stream channels for sending to other managers
            self._streams = []
            for _ in range(NUM_STREAMS_PER_MANAGER):
                self._streams.append(Channel.make_process_local())

            self._next_stream = 0
        except Exception as ex:
            log.debug("Exception caught while creating manager return channel for manager %s", self._manager_id)
            err_code = DragonError.FAILURE
            err_str = str(ex)
            self._register_with_orchestrator(serialized_return_orc, err_str=err_str, err_code=err_code)
            return

        # Create pool or attach to pool.
        # The manager attach to existing pool with serialized pool descriptor ser_pool_desc if restart is set
        # Otherwise, manager create a new pool and attach to it
        user = os.environ.get("USER", str(os.getuid()))
        self._pool_name = f"ddict_{self._name}_{self._manager_id}_{os.getpid()}_{self._puid}_{user}"
        self._traceit("self._pool_name=%s", self._pool_name)
        if self._restart and ser_pool_desc is not None:
            # attach to existing pool
            try:
                self._pool_sdesc = b64decode(ser_pool_desc)
                self._traceit("self._pool_sdesc=%s", self._pool_sdesc)
                self._pool = dmem.MemoryPool.attach(self._pool_sdesc)
                self._traceit("self._pool.muid=%s", self._pool.muid)
                self._pool_size = self._pool.free_space
            except dmem.DragonMemoryError as ex:
                tb = traceback.format_exc()
                log.debug(
                    "caught exception in manager %s while reattaching to memory pool. %s\n %s", self._manager_id, ex, tb
                )
                err_code = ex.rc
                err_str = str(ex)
                self._register_with_orchestrator(serialized_return_orc, err_str=err_str, err_code=err_code)
                return
            except Exception as ex:
                tb = traceback.format_exc()
                log.debug(
                    "caught exception in manager %s while reattaching to memory pool. %s\n %s", self._manager_id, ex, tb
                )
                err_code = DragonError.FAILURE
                err_str = (
                    f"caught exception in manager {self._manager_id} while reattaching to memory pool. {ex}\n {tb}"
                )
                self._register_with_orchestrator(serialized_return_orc, err_str=err_str, err_code=err_code)
                return

            # read BOOTSTRAP memory
            try:
                allocs = self._pool.get_allocations(alloc_type=dmem.AllocType.BOOTSTRAP)
                if allocs.num_allocs != 1:
                    raise RuntimeError("Could not find bootstrap memory")

                bootstrap_mem_alloc = self._pool.alloc_from_id(allocs.alloc_id(0))
                self._traceit("bootstrap_mem_alloc=%s", bootstrap_mem_alloc)
                bootstrap_mem_alloc_view = bootstrap_mem_alloc.get_memview()
            except dmem.DragonMemoryError as ex:
                tb = traceback.format_exc()
                log.debug(
                    "caught exception in manager %s while accessing bootstrap memory. %s\n %s", self._manager_id, ex, tb
                )
                err_code = ex.rc
                err_str = str(ex)
                self._register_with_orchestrator(serialized_return_orc, err_str=err_str, err_code=err_code)
                return
            except Exception as ex:
                tb = traceback.format_exc()
                log.debug(
                    "Failed to read bootstrap memeory. Manager %s losts all keys. %s\n %s", self._manager_id, ex, tb
                )
                err_code = DragonError.FAILURE
                err_str = f"Failed to read bootstrap memeory. Manager {self._manager_id} losts all keys. {ex}\n {tb}"
                self._register_with_orchestrator(serialized_return_orc, err_str=err_str, err_code=err_code)
                return

            # unpickle content in the BOOTSTRAP memory to repopulate manager, working set and checkpoints
            try:
                bootstrap_bytes = bootstrap_mem_alloc_view[:].tobytes()
                self._traceit("Content read from bootstrap mem")
                pickled_bootstrap_args = B64.bytes_to_str(bootstrap_bytes)
                bootstrap_args = cloudpickle.loads(b64decode(pickled_bootstrap_args))
                self.__setstate__(bootstrap_args)
                # free BOOTSTRAP memory after unpickle successfully
                bootstrap_mem_alloc.free()
                self._working_set.set_manager(self)

            except AssertionError as e:
                log.debug("Manager %s metadata mismatch: %s", self._manager_id, e)
                err_code = DragonError.FAILURE
                err_str = str(e)
                self._register_with_orchestrator(serialized_return_orc, err_str=err_str, err_code=err_code)
                return
            except Exception as ex:
                log.debug(
                    "Exception caught in manager %s while retrieving data from bootstrap memory.", self._manager_id
                )
                err_code = DragonError.FAILURE
                err_str = ex
                self._register_with_orchestrator(serialized_return_orc, err_str=err_str, err_code=err_code)
                return

            # If restarting, register the pool with Local Services now that restart was sucessful.
            self._pool.register(self._timeout)

        else:
            # create memory pool if not restart or if pool_desc is None during restart
            try:
                user = os.environ.get("USER", str(os.getuid()))
                self._pool_name = f"{facts.DEFAULT_DICT_POOL_NAME_BASE}_{os.getpid()}_{self._puid}_{user}"
                self._pool = dmem.MemoryPool.make_process_local(name=self._pool_name, size=pool_size)
                self._pool_size = self._pool.free_space
                self._pool_sdesc = self._pool.serialize()
            except Exception as ex:
                tb = traceback.format_exc()
                log.debug("Exception caught in manager %s while creating manager pool:%s\n%s", self._manager_id, ex, tb)
                err_code = DragonError.FAILURE
                err_str = str(ex)
                self._register_with_orchestrator(serialized_return_orc, err_str=err_str, err_code=err_code)
                return

        try:
            # We create these two channels in the default pool to isolate them
            # from the manager pool which could fill up. This is to make the
            # receiving of messages a bit more resistant to the manager pool
            # filling up.
            self._fli_main_channel = Channel.make_process_local()
            self._main_connector = fli.FLInterface(main_ch=self._fli_main_channel, pool=self._pool)
            self._serialized_main_connector = b64encode(self._main_connector.serialize())
            self._client_connections_map = {}
            self._buffered_client_connections_map = {}
            self._deferred_ops = {}
        except Exception as ex:
            log.debug("Exception caught in manager %s while creating manager.", self._manager_id)
            err_code = DragonError.FAILURE
            err_str = str(ex)
            self._register_with_orchestrator(serialized_return_orc, err_str=err_str, err_code=err_code)
            return

        # Working set is a map from chckpnt_id to a Tuple of (kvs, key_mem, deleted, persist) where kvs is the dictionary,
        # deleted are keys that are deleted from earlier checkpointed deleted keys, and persist is a set of keys
        # to persist when copying to newer checkpoints when wait_for_keys is true (otherwise all keys are persisted). The
        # key_mem is used to map to the key memory in the pool for clean up purposes.
        if not self._restart:
            self._working_set = WorkingSet(
                manager=self,
                move_to_pool=self._move_to_pool,
                deferred_ops=self._deferred_ops,
                working_set_size=self._working_set_size,
                wait_for_keys=self._wait_for_keys,
                wait_for_writers=self._wait_for_writers,
            )

        # send the manager information to local service and orchestrator to register manager
        self._register_with_local_service()

        self._register_with_orchestrator(serialized_return_orc, err_str=err_str, err_code=err_code)

    def __setstate__(self, args):
        # unpickle manager and check the metadata match the previous manager
        (wait_for_keys, wait_for_writers, working_set_size, persist_freq, self._working_set) = args
        assert (
            self._wait_for_keys == wait_for_keys
        ), f"wait_for_keys mismatch: passed {self._wait_for_keys}, got {wait_for_keys}"
        assert (
            self._wait_for_writers == wait_for_writers
        ), f"wait_for_writers mismatch: passed {self._wait_for_writers}, got {wait_for_writers}"
        assert (
            self._working_set_size == working_set_size
        ), f"working_set_size mismatch: passed {self._working_set_size}, got {working_set_size}"
        assert (
            self._persist_freq == persist_freq
        ), f"persist_freq mismatch: passed {self._persist_freq}, got {persist_freq}"
        # initiate working set and checkpoints as move_to_pool was not pickled. Pickling a function from manager leads to cyclic
        # pickling structure.
        self._working_set._move_to_pool = self._move_to_pool
        for chkpt_id in self._working_set._chkpts:
            self._working_set._chkpts[chkpt_id].set_pool_mover(self._move_to_pool)

    def __getstate__(self):
        return (
            self._wait_for_keys,
            self._wait_for_writers,
            self._working_set_size,
            self._persist_freq,
            self._working_set,
        )

    def _next_strm_channel(self):
        ch = self._streams[self._next_stream]
        self._next_stream = (self._next_client_id + 1) % NUM_STREAMS_PER_MANAGER
        return ch

    def _traceit(self, *args, **kw_args):
        if self._trace:
            log.log(logging.INFO, *args, **kw_args)

    def _cleanup(self):
        # We do not clean up the pool because it will be cleaned up by local services automatically when the manager
        # exits (if we did not deregister it for a restart situation).
        try:
            self._main_connector.destroy()
            self._fli_main_channel.destroy()
        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "manager %s with puid=%s failed to destroy main FLI. Exception:%s\nTraceback:%s\n",
                self._manager_id,
                self._puid,
                ex,
                tb,
            )

    def _free_resources(self):

        try:
            # destroy all client maps
            for i in self._buffered_client_connections_map:
                self._buffered_client_connections_map[i].detach()
            del self._buffered_client_connections_map
            for i in self._client_connections_map:
                self._client_connections_map[i].detach()
            for i in range(len(self._managers)):
                if i != self._manager_id:
                    self._manager_flis[i].detach()
            del self._client_connections_map

            # pickle manager if allow restart is set
            if self._allow_restart:
                self._pool.deregister()  # deregistering allows the pool to remain on the node following manager exit.
                log.debug("The manager was brought down with allow_restart set to true.")
                meta_data = b64encode(cloudpickle.dumps(self.__getstate__()))
                ret_bytes = B64.str_to_bytes(meta_data)
                # allocate bootstrap memory and write data into the memory
                bootstrap_mem = self._pool.alloc(size=len(ret_bytes), alloc_type=dmem.AllocType.BOOTSTRAP)
                bootstrap_mem_view = bootstrap_mem.get_memview()
                bootstrap_mem_view[:] = ret_bytes
                self._traceit("Content written to bootstrap mem")
            else:
                # Destroy the manager's FLIs
                self._cleanup()

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug("manager %s failed to destroy resources. Exception: %s\n Traceback: %s\n", self._puid, ex, tb)

    def _register_with_local_service(self):
        log.debug("manager is sending set_local_kv with self._serialized_main_orc=%s", self._serialized_main_orc)
        set_local_kv(key=self._serialized_main_orc, value=self._serialized_main_connector)

    def _tag_inc(self):
        tag = self._tag
        self._tag += 1
        return tag

    def _iter_inc(self):
        iter_id = self._iter_id
        self._iter_id += 1
        return iter_id

    def _move_to_pool(self, client_mem):
        if client_mem.pool.muid != self._pool.muid:
            # we need to move it - if no room don't wait.
            try:
                new_mem = client_mem.copy(self._pool, timeout=0)
                log.debug("Manager was required to copy value to pool. This should not happen!")
            except dmem.DragonMemoryError:
                raise DDictManagerFull(DragonError.MEMORY_POOL_FULL, "Could not move data to manager pool.")
            finally:
                client_mem.free()

            return new_mem

        return client_mem

    def _defer(self, dictop: DictOp):
        if dictop.chkpt_id not in self._deferred_ops:
            self._deferred_ops[dictop.chkpt_id] = []
        self._traceit("Operation deferred: %s", dictop)
        self._deferred_ops[dictop.chkpt_id].append(dictop)

    def _process_deferred_ops(self, chkpt_id: int):
        if chkpt_id in self._deferred_ops:
            left_overs = []
            while len(self._deferred_ops[chkpt_id]) > 0:
                op = self._deferred_ops[chkpt_id].pop(0)
                performed = op.perform()
                if not performed:
                    left_overs.append(op)
                else:
                    self._traceit("Deferred Operation now complete %s", op)

            if len(left_overs) == 0:
                # All performed.
                del self._deferred_ops[chkpt_id]
            else:
                self._deferred_ops[chkpt_id] = left_overs

    def _recv_and_check_msg_ref(self, expected_ref: int, recvh):
        ref = -1
        while ref != expected_ref:
            resp_ser_msg, hint = recvh.recv_bytes(timeout=self._timeout)
            resp_msg = dmsg.parse(resp_ser_msg)
            self._traceit("Response: %s", resp_msg)
            ref = resp_msg.ref
            if ref != expected_ref:
                log.info("Tossing lost/timed out message in manager %s: %s", self._puid, resp_msg)
            else:
                return resp_msg, hint

    def _recv_msg(self, expected_ref: int):
        with self._buffered_return_connector.recvh(destination_pool=self._pool) as recvh:
            # Wait patiently here since it might be a big dictionary and is
            # just starting.
            resp_msg, hint = self._recv_and_check_msg_ref(expected_ref, recvh)

        return resp_msg

    def _send_msg(self, msg, connection):
        try:
            if connection.is_buffered:
                strm = None
            else:
                strm = self._next_strm_channel()

            with connection.sendh(timeout=self._timeout, stream_channel=strm) as sendh:
                sendh.send_bytes(msg.serialize(), timeout=self._timeout)
        except Exception as ex:
            tb = traceback.format_exc()
            log.debug("There was an exception in the manager _send_msg: %s\n Traceback: %s", ex, tb)
            raise RuntimeError(f"There was an exception in the manager _send_msg: {ex} \n Traceback: {tb}")

    def _send_dmsg_and_value(
        self, chkpt: Checkpoint, resp_msg, connection, key_mem: dmem.MemoryAlloc, transfer_ownership=False
    ) -> None:
        with connection.sendh(use_main_as_stream_channel=True, timeout=self._timeout) as sendh:
            sendh.send_bytes(resp_msg.serialize(), timeout=self._timeout)

            if resp_msg.err == DragonError.SUCCESS:
                val_list = chkpt.map[key_mem]
                if transfer_ownership:
                    chkpt.map[key_mem] = []
                for val in val_list:
                    sendh.send_mem(val, transfer_ownership=transfer_ownership, arg=VALUE_HINT, timeout=self._timeout)
                if transfer_ownership:
                    del chkpt.map[key_mem]
                    if key_mem not in chkpt.persist:
                        del chkpt.key_allocs[key_mem]
                        self.check_for_key_existence_before_free(key_mem)
                    else:
                        chkpt.deleted.add(key_mem)
                        chkpt.persist.remove(key_mem)

    def _send_dmsg_and_keys(self, resp_msg, connection, keys: list) -> None:
        with connection.sendh(use_main_as_stream_channel=True, timeout=self._timeout) as sendh:
            sendh.send_bytes(resp_msg.serialize(), timeout=self._timeout)
            if resp_msg.err == DragonError.SUCCESS:
                for key in keys:
                    sendh.send_mem(key, transfer_ownership=False, arg=KEY_HINT, timeout=self._timeout)

    def _send_dmsg_to_children(self, msg) -> None:
        left_child = 2 * self._manager_id + 1
        right_child = 2 * self._manager_id + 2

        if left_child < len(self._managers):
            self._send_msg(msg, self._manager_flis[left_child])

        if right_child < len(self._managers):
            self._send_msg(msg, self._manager_flis[right_child])

    def _register_with_orchestrator(self, serialized_return_orc: str, err_str="", err_code=DragonError.SUCCESS):
        if err_code == DragonError.SUCCESS:
            msg = dmsg.DDRegisterManager(
                self._tag_inc(),
                self._manager_id,
                self._serialized_main_connector,
                self._serialized_buffered_return_connector,
                self._host_id,
                b64encode(self._pool_sdesc),
                errInfo=err_str,
                err=err_code,
            )
            log.debug("sent DDRegisterManager")
        else:
            msg = dmsg.DDRegisterManager(
                self._tag_inc(),
                self._manager_id,
                "",
                self._serialized_buffered_return_connector,
                "",
                self._host_id,
                "",
                errInfo=err_str,
                err=err_code,
            )

        connection = fli.FLInterface.attach(b64decode(serialized_return_orc))
        self._send_msg(msg, connection)
        connection.detach()
        log.debug("about to receive response DDRegisterManagerResponse")
        resp_msg = self._recv_msg(msg.tag)
        if resp_msg.err != DragonError.SUCCESS:
            raise Exception(f"Failed to register manager with orchester. Return code: {resp_msg.err}")
        self._managers = resp_msg.managers
        log.debug("The number of managers is %s", len(self._managers))
        self._serialized_manager_nodes = resp_msg.managerNodes
        for serialized_node in self._serialized_manager_nodes:
            self._manager_hostnames.append(cloudpickle.loads(b64decode(serialized_node)).hostname)
        for i in range(len(self._managers)):
            if i != self._manager_id:
                self._manager_flis[i] = fli.FLInterface.attach(b64decode(self._managers[i]))

            self._next_client_id = self._manager_id * MAX_NUM_CLIENTS_PER_MANAGER + 1
            self._serving = True
            self._bytes_for_dict = self._pool.free_space
            self._registered = True
            self._serialized_manager_nodes = resp_msg.managerNodes

    def _register_client(self, client_id: int, respFLI: str, bufferedRespFLI: str):
        self._client_connections_map[client_id] = fli.FLInterface.attach(b64decode(respFLI))
        self._buffered_client_connections_map[client_id] = fli.FLInterface.attach(b64decode(bufferedRespFLI))

    def _get_next_client_id(self):
        client_id = self._next_client_id
        self._next_client_id += 1
        return client_id

    def _recover_mem(self, client_key_mem: dmem.MemoryAlloc, val_list: list, recvh):
        # Depending on where we got to, these two free's may fail, that's OK.
        log.info("Attempting to recover memory.")
        try:
            self.check_for_key_existence_before_free(client_key_mem)
        except:
            pass

        while len(val_list) > 0:
            val = val_list.pop()
            try:
                val.free()
            except:
                pass

        if not recvh.stream_received:
            try:
                while True:
                    try:
                        mem, hint = recvh.recv_mem(timeout=self._timeout)
                        mem.free()
                    except fli.DragonFLIOutOfMemoryError:
                        log.info("Got OUT OF MEM")
            except EOFError:
                log.info("Got EOF")
            except Exception as ex:
                tb = traceback.format_exc()
                log.debug("Caught exception while discarding rest of stream: %s\n %s", ex, tb)

        log.info("Now returning from recover mem")

    def check_for_key_existence_before_free(self, key):
        self._working_set.check_for_key_existence_before_free(key)

    def run(self):
        try:
            while self._serving:
                with self._main_connector.recvh(destination_pool=self._pool) as recvh:
                    try:
                        ser_msg, hint = recvh.recv_bytes()
                        msg = dmsg.parse(ser_msg)
                        self._traceit("About to process: %s", msg)
                        if type(msg) in self._DTBL:
                            self._DTBL[type(msg)][0](self, msg=msg, recvh=recvh)
                            self._traceit("Finished processing: %s", msg)
                        else:
                            self._serving = False
                            self._abnormal_termination = True
                            log.debug("The message %s is not a valid message!", msg)
                    except EOFError:
                        log.info("Got EOFError")
                    except fli.DragonFLIRecvdMsgDestroyedError as ex:
                        tb = traceback.format_exc()
                        log.debug(
                            "Could not receive message because underlying memory was destroyed:\n%s\n Traceback:\n%s",
                            ex,
                            tb,
                        )

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug("There was an exception in manager:\n%s\n Traceback:\n%s", ex, tb)

        try:
            # Because there are potentially many of DDDestroy requests sent, the
            # orchestrator will get overwhelmed with pending
            # responses if we hold onto the receive handle and try to
            # send response at the same time. The issue is that the
            # orchestrator as one stream channel and that stream
            # channel is not re-usable until the receive handle is
            # closed. HOWEVER, if we hold open the receive handle AND
            # the orc's response queue also fills with pending
            # responses, then we are in a deadlock. So we respond
            # here after we have closed the receive handle.
            set_local_kv(key=self._serialized_main_orc, value="")
            resp_msg = dmsg.DDDestroyManagerResponse(self._tag_inc(), ref=msg._tag, err=DragonError.SUCCESS)
            connection = fli.FLInterface.attach(b64decode(self._serialized_return_orc))
            self._send_msg(resp_msg, connection)
            connection.detach()

            log.info("Manager %s preparing to exit", self._manager_id)
            log.info("Other manager hostnames: %s", self._manager_hostnames)
            log.info("Pool utilization percent is %s", self._pool.utilization)
            # self._pool.free_blocks is a map where keys are the memory block sizes and values are number of blocks with the size.
            log.info(
                "Free memory blocks, keys are memory block sizes and values are the number of blocks with that particular size:"
            )
            for free_block_key in self._pool.free_blocks.keys():
                log.info("%s: %s", free_block_key, self._pool.free_blocks[free_block_key])
            # TBD fix this so we can get more stats.
            # log.info(f'Number of keys stored is {len(self._map)}')
            log.info("Free space is %s", self._pool.free_space)
            log.info("The total size of the pool managed by this manager was %s", self._pool.size)
        except Exception as ex:
            tb = traceback.format_exc()
            log.debug("There was an exception in the manager while free resources:\n%s\n Traeback:\n%s", ex, tb)

        try:
            self._free_resources()
        except Exception as ex:
            tb = traceback.format_exc()
            log.debug("There was an exception in the manager while free resources:\n%s\n Traeback:\n%s", ex, tb)

    @dutil.route(dmsg.DDRegisterClient, _DTBL)
    def register_client(self, msg: dmsg.DDRegisterClient, recvh):
        try:
            client_id = self._get_next_client_id()
            self._register_client(client_id=client_id, respFLI=msg.respFLI, bufferedRespFLI=msg.bufferedRespFLI)
            resp_msg = dmsg.DDRegisterClientResponse(
                self._tag_inc(),
                ref=msg.tag,
                err=DragonError.SUCCESS,
                clientID=client_id,
                numManagers=len(self._managers),
                managerID=self._manager_id,
                managerNodes=self._serialized_manager_nodes,
                name=self._name,
                timeout=self._timeout,
            )
            self._send_msg(resp_msg, self._buffered_client_connections_map[client_id])
        except Exception as ex:
            tb = traceback.format_exc()
            log.debug("GOT EXCEPTION %s", tb)
            log.debug(
                "There was an exception in the register_client to manager %s for client %s: %s\n Traceback: %s\n%s",
                self._puid,
                self._global_client_id,
                ex,
                tb,
                msg.respFLI,
            )

    @dutil.route(dmsg.DDConnectToManager, _DTBL)
    def connect_to_manager(self, msg: dmsg.DDConnectToManager, recvh):
        try:
            resp_msg = dmsg.DDConnectToManagerResponse(
                self._tag_inc(), ref=msg.tag, err=DragonError.SUCCESS, manager=self._managers[msg.managerID]
            )
            self._send_msg(resp_msg, self._buffered_client_connections_map[msg.clientID])
        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an exception in request manager %s from manager %s for client %s: %s \n Traceback: %s\n%s",
                msg.managerID,
                self._puid,
                msg.clientID,
                ex,
                tb,
                msg.respFLI,
            )
            raise RuntimeError(
                f"There was an exception in request manager {msg.managerID} from manager {self._puid=} for client {msg.clientID}: {ex} \n Traceback: {tb}\n {msg.respFLI=}"
            )

    @dutil.route(dmsg.DDRegisterClientID, _DTBL)
    def register_clientID(self, msg: dmsg.DDRegisterClientID, recvh):
        try:
            self._register_client(client_id=msg.clientID, respFLI=msg.respFLI, bufferedRespFLI=msg.bufferedRespFLI)
            resp_msg = dmsg.DDRegisterClientIDResponse(self._tag_inc(), ref=msg.tag, err=DragonError.SUCCESS)
            self._send_msg(resp_msg, self._buffered_client_connections_map[msg.clientID])
        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an exception in the register_clientID to manager %s for client %s: %s\n Traceback: %s\n%s",
                self._puid,
                msg.clientID,
                ex,
                tb,
                msg.respFLI,
            )
            raise RuntimeError(
                f"There was an exception in the register_clientID to manager {self._puid=} for client {msg.clientID}: {ex} \n Traceback: {tb}\n {msg.respFLI=}"
            )

    @dutil.route(dmsg.DDDestroyManager, _DTBL)
    def destroy_manager(self, msg: dmsg.DDDestroyManager, recvh):
        try:
            self._serving = False
            self._allow_restart = msg.allowRestart
        except Exception as ex:
            tb = traceback.format_exc()
            log.debug("There was an exception while destroying manager %s: %s\n Traceback: %s", self._puid, ex, tb)

    @dutil.route(dmsg.DDPut, _DTBL)
    def put(self, msg: dmsg.DDPut, recvh):
        client_key_mem = None
        val_list = []

        try:
            try:
                if self._pool.utilization >= 90.0 or self._pool.free_space < RESERVED_POOL_SPACE:
                    raise DDictManagerFull(
                        DragonError.MEMORY_POOL_FULL, f"DDict Manager {self._manager_id}: Pool reserve limit exceeded."
                    )

                log.debug("Getting Key")

                # There is likely room for the key/value pair.
                client_key_mem, hint = recvh.recv_mem(timeout=self._timeout)

                assert hint == KEY_HINT

                log.debug("Got Key")

                try:
                    while True:
                        val_mem, hint = recvh.recv_mem(timeout=self._timeout)
                        val_mem = self._move_to_pool(val_mem)
                        assert hint == VALUE_HINT
                        val_list.append(val_mem)
                except EOFError:
                    pass

                log.debug("Completed Put")

                persist = msg.persist and self._wait_for_keys
                put_op = PutOp(self, msg.clientID, msg.chkptID, msg.tag, persist, client_key_mem, val_list)

                # advance the checkpoint if it is possible to the new checkpoint ID
                if self._working_set.put(msg.chkptID) is not None:
                    # process any earlier get or put requests first that can be performed
                    self._process_deferred_ops(msg.chkptID)
                if not put_op.perform():
                    # We must wait for the checkpoint to exist in this case
                    self._defer(put_op)
                else:
                    # if there's any get for this key, then process deferred gets
                    self._process_deferred_ops(msg.chkptID)

            except (DDictManagerFull, fli.DragonFLIOutOfMemoryError) as ex:
                log.info("Manager %s with PUID=%s could not process put request. %s", self._manager_id, self._puid, ex)
                # recover from the error by freeing memory and cleaning recvh.
                log.info("About to recover memory")
                self._recover_mem(client_key_mem, val_list, recvh)
                log.info("Streamed data now recovered. Sending put response to indicate failure.")
                resp_msg = dmsg.DDPutResponse(self._tag_inc(), ref=msg.tag, err=DragonError.MEMORY_POOL_FULL)
                self._send_msg(resp_msg, self._buffered_client_connections_map[msg.clientID])

            except DDictCheckpointSync as ex:
                log.info("Manager %s with PUID=%s could not process put request. %s", self._manager_id, self._puid, ex)
                log.info(
                    "The requested put operation for checkpoint id %s was older than the working set range of %s",
                    msg.chkptID,
                    self._working_set.range,
                )
                # recover from the error by freeing memory and cleaning recvh.
                self._recover_mem(client_key_mem, val_list, recvh)
                resp_msg = dmsg.DDPutResponse(
                    self._tag_inc(),
                    ref=msg.tag,
                    err=DragonError.DDICT_CHECKPOINT_RETIRED,
                    errInfo=f"The requested put operation for checkpoint id {msg.chkptID} was older than the working set range of {self._working_set.range}",
                )
                self._send_msg(resp_msg, self._buffered_client_connections_map[msg.clientID])

            except Exception as ex:
                tb = traceback.format_exc()
                log.info(
                    "Manager %s with PUID=%s could not process put request. %s\n %s",
                    self._manager_id,
                    self._puid,
                    ex,
                    tb,
                )
                # recover from the error by freeing memory and cleaning recvh.
                self._recover_mem(client_key_mem, val_list, recvh)
                resp_msg = dmsg.DDPutResponse(
                    self._tag_inc(), ref=msg.tag, err=DragonError.FAILURE, errInfo="Manager Exception: " + str(ex)
                )
                self._send_msg(resp_msg, self._buffered_client_connections_map[msg.clientID])

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an unexpected exception in put in the manager, %s, %s: %s\n Traceback: %s",
                self._puid,
                msg.clientID,
                ex,
                tb,
            )
            raise RuntimeError(
                f"There was an unexpected exception in put in manager, {self._puid=}, {msg.clientID=}: {ex} \n Traceback: {tb}"
            )

    @dutil.route(dmsg.DDGet, _DTBL)
    def get(self, msg: dmsg.DDGet, recvh):
        try:
            client_key_mem, hint = recvh.recv_mem(timeout=self._timeout)
            assert hint == KEY_HINT

            get_op = GetOp(self, msg.clientID, msg.chkptID, msg.tag, client_key_mem)

            if not get_op.perform():
                self._defer(get_op)

        except (DDictManagerFull, fli.DragonFLIOutOfMemoryError) as ex:
            log.info("Manager %s with PUID=%s could not process get request. %s", self._manager_id, self._puid, ex)
            log.info("The requested get operation could not be completed because the manager pool is too full")
            # recover from the error by freeing memory and cleaning recvh.
            self._recover_mem(client_key_mem, [], recvh)
            resp_msg = dmsg.DDGetResponse(
                self._tag_inc(),
                ref=msg.tag,
                err=DragonError.MEMORY_POOL_FULL,
                errInfo=f"The requested get operation could not be completed. The manager pool is full.",
            )
            self._send_dmsg_and_value(
                chkpt=msg.chkptID,
                resp_msg=resp_msg,
                connection=self._client_connections_map[msg.clientID],
                key_mem=None,
            )

        except DDictCheckpointSync as ex:
            log.info("Manager %s with PUID=%s could not process get request. %s", self._manager_id, self._puid, ex)
            log.info(
                "The requested get operation for checkpoint id %s was older than the working set range of %s",
                msg.chkptID,
                self._working_set.range,
            )
            # recover from the error by freeing memory and cleaning recvh.
            self._recover_mem(client_key_mem, [], recvh)
            resp_msg = dmsg.DDGetResponse(
                self._tag_inc(),
                ref=msg.tag,
                err=DragonError.DDICT_CHECKPOINT_RETIRED,
                errInfo=f"The requested get operation for checkpoint id {msg.chkptID} was older than the working set range of {self._working_set.range}",
            )
            self._send_dmsg_and_value(
                chkpt=msg.chkptID,
                resp_msg=resp_msg,
                connection=self._client_connections_map[msg.clientID],
                key_mem=None,
            )

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an unexpected exception in get in the manager,%s, %s: %s\nTraceback: %s",
                self._puid,
                msg.clientID,
                ex,
                tb,
            )
            raise RuntimeError(
                f"There was an unexpected exception in get in manager, {self._puid=}, {msg.clientID=}: {ex} \n Traceback: {tb}"
            )

    @dutil.route(dmsg.DDPop, _DTBL)
    def pop(self, msg: dmsg.DDPop, recvh):
        try:
            key_mem, hint = recvh.recv_mem(timeout=self._timeout)
            assert hint == KEY_HINT

            pop_op = PopOp(self, msg.clientID, msg.chkptID, msg.tag, key_mem)

            if not pop_op.perform():
                self._defer(pop_op)

        except DDictCheckpointSync as ex:
            log.info("Manager %s with PUID=%s could not process get request. %s", self._manager_id, self._puid, ex)
            log.info(
                "The requested pop operation for checkpoint id %s was older than the working set range of %s",
                msg.chkptID,
                self._working_set.range,
            )
            # recover from the error by freeing memory and cleaning recvh.
            self._recover_mem(key_mem, [], recvh)
            resp_msg = dmsg.DDPopResponse(
                self._tag_inc(),
                ref=msg.tag,
                err=DragonError.DDICT_CHECKPOINT_RETIRED,
                errInfo=f"The requested pop operation for checkpoint id {msg.chkptID} was older than the working set range of {self._working_set.range}",
            )
            self._send_dmsg_and_value(
                chkpt=msg.chkptID,
                resp_msg=resp_msg,
                connection=self._client_connections_map[msg.clientID],
                key_mem=None,
            )

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an unexpected exception in pop in the manager %s, %s: %s \n Traceback: %s",
                self._puid,
                msg.clientID,
                ex,
                tb,
            )
            raise RuntimeError(
                f"There was an unexpected exception in pop in manager, {self._puid=}, {msg.clientID=}: {ex} \n Traceback: {tb}"
            )

    @dutil.route(dmsg.DDContains, _DTBL)
    def contains(self, msg: dmsg.DDContains, recvh):
        try:
            key_mem, hint = recvh.recv_mem(timeout=self._timeout)
            assert hint == KEY_HINT

            contains_op = ContainsOp(self, msg.clientID, msg.chkptID, msg.tag, key_mem)

            contains_op.perform()

        except (DDictManagerFull, fli.DragonFLIOutOfMemoryError) as ex:
            log.info("Manager %s with PUID=%s could not process get request. %s", self._manager_id, self._puid, ex)
            log.info("The requested get operation could not be completed because the manager pool is too full")
            # recover from the error by freeing memory and cleaning recvh.
            self._recover_mem(key_mem, [], recvh)
            resp_msg = dmsg.DDContainsResponse(
                self._tag_inc(),
                ref=msg.tag,
                err=DragonError.MEMORY_POOL_FULL,
                errInfo=f"The requested get operation could not be completed. The manager pool is full.",
            )
            self._send_dmsg_and_value(
                chkpt=msg.chkptID,
                resp_msg=resp_msg,
                connection=self._client_connections_map[msg.clientID],
                key_mem=None,
            )

        except DDictCheckpointSync as ex:
            log.info("Manager %s with PUID=%s could not process contains request. %s", self._manager_id, self._puid, ex)
            log.info(
                "The requested contains operation for checkpoint id %s was older than the working set range of %s",
                msg.chkptID,
                self._working_set.range,
            )
            # recover from the error by freeing memory and cleaning recvh.
            self._recover_mem(key_mem, [], recvh)
            resp_msg = dmsg.DDContainsResponse(
                self._tag_inc(),
                ref=msg.tag,
                err=DragonError.DDICT_CHECKPOINT_RETIRED,
                errInfo=f"The requested contains operation for checkpoint id {msg.chkptID} was older than the working set range of {self._working_set.range}",
            )
            self._send_dmsg_and_value(
                chkpt=msg.chkptID,
                resp_msg=resp_msg,
                connection=self._client_connections_map[msg.clientID],
                key_mem=None,
            )

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an unexpected exception in contains in the manager, %s, %s: %s \n Traceback: %s",
                self._puid,
                msg.clientID,
                ex,
                tb,
            )
            raise RuntimeError(
                f"There was an unexpected exception in contains in manager, {self._puid=}, {msg.clientID=}: {ex} \n Traceback: {tb}"
            )

    @dutil.route(dmsg.DDLength, _DTBL)
    def get_length(self, msg: dmsg.DDLength, recvh):
        try:
            if msg.broadcast:
                self._send_dmsg_to_children(msg)

            length_op = LengthOp(self, msg.clientID, msg.chkptID, msg.tag, msg.respFLI)

            length_op.perform()

        except DDictCheckpointSync as ex:
            log.info("Manager %s with PUID=%s could not process length request. %s", self._manager_id, self._puid, ex)
            log.info(
                "The requested length operation for checkpoint id %s was older than the working set range of %s",
                msg.chkptID,
                self._working_set.range,
            )
            resp_msg = dmsg.DDLengthResponse(
                self._tag_inc(),
                ref=msg.tag,
                err=DragonError.DDICT_CHECKPOINT_RETIRED,
                errInfo=f"The requested length operation for checkpoint id {msg.chkptID} was older than the working set range of {self._working_set.range}",
            )
            self._send_msg(resp_msg, self._buffered_client_connections_map[self.client_id])

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug("There was an exception in get_length from manager %s: %s\n Traeback: \n%s", self._puid, ex, tb)
            raise RuntimeError(
                f"There was an exception in get_length from manager {self._puid}: {ex} \n Traeback: \n {tb}"
            )

    @dutil.route(dmsg.DDClear, _DTBL)
    def clear(self, msg: dmsg.DDClear, recvh):
        try:
            if msg.broadcast:
                self._send_dmsg_to_children(msg)

            clear_op = ClearOp(self, msg.clientID, msg.chkptID, msg.tag, msg.respFLI)

            if not clear_op.perform():
                self._defer(clear_op)

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an unexpected exception in clear in the manager, %s, %s: %s \n Traceback: %s",
                self._puid,
                msg.clientID,
                ex,
                tb,
            )
            raise RuntimeError(
                f"There was an unexpected exception in clear in manager, {self._puid=}, {msg.clientID=}: {ex} \n Traceback: {tb}"
            )

    @dutil.route(dmsg.DDManagerStats, _DTBL)
    def get_stats(self, msg: dmsg.DDManagerStats, recvh):
        try:
            if msg.broadcast:
                self._send_dmsg_to_children(msg)

            stats = DDictManagerStats(
                manager_id=self._manager_id,
                hostname=socket.gethostname(),
                total_bytes=self._pool_size,
                total_used_bytes=self._pool_size - self._pool.free_space,
                pool_free_space=self._pool.free_space,
                pool_utilization=self._pool.utilization,
                num_keys=self._working_set.key_count,
                free_blocks=self._pool.free_blocks,
                max_pool_allocations=self._pool.max_allocations,
                max_pool_allocations_used=self._pool.max_used_allocations,
                current_pool_allocations_used=self._pool.current_allocations,
            )

            data = b64encode(cloudpickle.dumps(stats))
            resp_msg = dmsg.DDManagerStatsResponse(self._tag_inc(), ref=msg.tag, data=data, err=DragonError.SUCCESS)
            connection = fli.FLInterface.attach(b64decode(msg.respFLI))
            self._send_msg(resp_msg, connection)
            connection.detach()

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an unexpected exception in get_stats in the manager, %s, %s: %s \n Traceback: %s",
                self._puid,
                msg.clientID,
                ex,
                tb,
            )
            raise RuntimeError(
                f"There was an unexpected exception in get_stats in manager, {self._puid=}, {msg.clientID=}: {ex} \n Traceback: {tb}"
            )

    @dutil.route(dmsg.DDManagerNewestChkptID, _DTBL)
    def get_newest_chkpt_id(self, msg: dmsg.DDManagerNewestChkptID, recvh):
        try:
            if msg.broadcast:
                self._send_dmsg_to_children(msg)

            chkpt_id = self._working_set.newest_chkpt_id

            resp_msg = dmsg.DDManagerNewestChkptIDResponse(
                self._tag_inc(), ref=msg.tag, chkptID=chkpt_id, err=DragonError.SUCCESS
            )
            connection = fli.FLInterface.attach(b64decode(msg.respFLI))
            self._send_msg(resp_msg, connection)
            connection.detach()

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an unexpected exception in get_newest_chkpt_id in the manager, %s, %s: %s \n Traceback: %s",
                self._puid,
                msg.clientID,
                ex,
                tb,
            )
            raise RuntimeError(
                f"There was an unexpected exception in get_newest_chkpt_id in manager, {self._puid=}, {msg.clientID=}: {ex} \n Traceback: {tb}"
            )

    @dutil.route(dmsg.DDIterator, _DTBL)
    def get_iterator(self, msg: dmsg.DDIterator, recvh):
        pass

    @dutil.route(dmsg.DDIteratorNext, _DTBL)
    def iterate_next(self, msg: dmsg.DDIteratorNext, recvh):
        with self._client_connections_map[msg.clientID].sendh(
            use_main_as_stream_channel=True, timeout=self._timeout
        ) as sendh:
            try:
                key = next(self.iterators[msg.iterID])
                resp_msg = dmsg.DDIteratorNextResponse(self._tag_inc(), ref=msg.tag, err=DragonError.SUCCESS)
                sendh.send_bytes(resp_msg.serialize(), timeout=self._timeout)
                sendh.send_mem(key, transfer_ownership=False, arg=KEY_HINT, timeout=self._timeout)
            except StopIteration:
                resp_msg = dmsg.DDIteratorNextResponse(self._tag_inc(), ref=msg.tag, err=DragonError.NO_MORE_KEYS)
                del self.iterators[msg.iterID]
                sendh.send_bytes(resp_msg.serialize(), timeout=self._timeout)

    @dutil.route(dmsg.DDKeys, _DTBL)
    def keys(self, msg: dmsg.DDKeys, recvh):
        try:
            keys_op = KeysOp(self, msg.clientID, msg.chkptID, msg.tag)

            keys_op.perform()

        except DDictCheckpointSync as ex:
            log.info("Manager %s with PUID=%s could not process keys request. %s", self._manager_id, self._puid, ex)
            log.info(
                "The requested keys operation for checkpoint id %s was older than the working set range of %s",
                msg.chkptID,
                self._working_set.range,
            )
            resp_msg = dmsg.DDKeysResponse(
                self._tag_inc(),
                ref=msg.tag,
                err=DragonError.DDICT_CHECKPOINT_RETIRED,
                errInfo=f"The requested keys operation for checkpoint id {msg.chkptID} was older than the working set range of {self._working_set.range}",
            )
            self._send_dmsg_and_keys(resp_msg, self._client_connections_map[self.client_id], None)

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an unexpected exception in keys in the manager, %s, %s: %s \n Traceback: %s",
                self._puid,
                msg.clientID,
                ex,
                tb,
            )
            raise RuntimeError(
                f"There was an unexpected exception in keys in manager, {self._puid=}, {msg.clientID=}: {ex} \n Traceback: {tb}"
            )

    @dutil.route(dmsg.DDDeregisterClient, _DTBL)
    def deregister_client(self, msg: dmsg.DDDeregisterClient, recvh):
        try:
            self._client_connections_map[msg.clientID].detach()
            del self._client_connections_map[msg.clientID]

            resp_msg = dmsg.DDDeregisterClientResponse(self._tag_inc(), ref=msg.tag, err=DragonError.SUCCESS)
            self._send_msg(resp_msg, self._buffered_client_connections_map[msg.clientID])

            self._buffered_client_connections_map[msg.clientID].detach()
            del self._buffered_client_connections_map[msg.clientID]

        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an exception while deregistering client in manager. Exception: %s\n Traceback: %s", ex, tb
            )

    @dutil.route(dmsg.DDManagerSync, _DTBL)
    def manager_sync(self, msg: dmsg.DDManagerSync, recvh):
        # Send message to the full manager to request state.
        mgr_get_state_req = dmsg.DDManagerGetState(self._tag_inc(), respFLI=self._serialized_return_connector)
        connection = fli.FLInterface.attach(b64decode(msg.fullManagerFLI))
        self._send_msg(mgr_get_state_req, connection)
        connection.detach()
        log.debug("about to receive response DDManagerGetStateResponse")
        indirect = dict()
        # Receive state from the full manager.
        with self._return_connector.recvh(use_main_as_stream_channel=True, timeout=self._timeout) as recvh:

            resp_msg, hint = self._recv_and_check_msg_ref(mgr_get_state_req.tag, recvh)

            if resp_msg.err != DragonError.SUCCESS:
                log.debug("There was an exception in manager sync with manager %s.\n %s", self._puid, resp_msg.err_info)
                raise RuntimeError(
                    f"There was an exception in manager sync with manager {self._puid}.\n {resp_msg.err_info}"
                )

            self.__setstate__(cloudpickle.loads(b64decode(resp_msg.state)))
            self._working_set.set_manager(self)
            # Receive streamed mem id and memory
            try:
                while True:
                    pickled_id, hint = recvh.recv_bytes(timeout=self._timeout)
                    mem, hint = recvh.recv_mem(timeout=self._timeout)
                    # key: id from the full manager, value: the memory in new pool of the empty manager
                    id = cloudpickle.loads(pickled_id)
                    indirect[id] = mem
            except EOFError:
                pass
            except Exception as ex:
                tb = traceback.format_exc()
                log.debug(
                    "There was an exception in manager %s while receiving stream memory: %s \n Traceback: %s",
                    self._puid,
                    ex,
                    tb,
                )
                raise RuntimeError(
                    f"There was an exception in manager {self._puid} while receiving stream memory: {ex} \n Traceback: {tb}"
                )

        try:
            # Repopulate maps of each checkpoint with the memory
            self._working_set.redirect(indirect)

            # Successfully received and filled the empty manager, returning response to client.
            ret_resp_msg = dmsg.DDManagerSyncResponse(self._tag_inc(), ref=msg.tag, err=DragonError.SUCCESS)
            connection = fli.FLInterface.attach(b64decode(msg.respFLI))
            self._send_msg(ret_resp_msg, connection)
            connection.detach()
        except Exception as ex:
            tb = traceback.format_exc()
            log.debug(
                "There was an exception in manager %s while receiving stream memory: %s \n Traceback: %s",
                self._puid,
                ex,
                tb,
            )
            raise RuntimeError(
                f"There was an exception in manager {self._puid} while receiving stream memory: {ex} \n Traceback: {tb}"
            )

    @dutil.route(dmsg.DDManagerGetState, _DTBL)
    def manager_get_state(self, msg: dmsg.DDManagerGetState, recvh):
        try:
            self._reattach = False
            state = b64encode(cloudpickle.dumps(self.__getstate__()))
            self._reattach = True
            resp_msg = dmsg.DDManagerGetStateResponse(
                self._tag_inc(), ref=msg.tag, err=DragonError.SUCCESS, state=state
            )
            # Send response back and streamed key and value memory
            allocs = self._working_set.build_allocs()
            connection = fli.FLInterface.attach(b64decode(msg.respFLI))
            with connection.sendh(use_main_as_stream_channel=True, timeout=self._timeout) as sendh:
                sendh.send_bytes(resp_msg.serialize(), timeout=self._timeout)
                for id, mem in allocs.items():
                    sendh.send_bytes(cloudpickle.dumps(id), timeout=self._timeout)
                    sendh.send_mem(mem, transfer_ownership=False, timeout=self._timeout)
            connection.detach()
        except Exception as ex:
            tb = traceback.format_exc()
            log.debug("GOT EXCEPTION %s", tb)
            log.debug(
                "There was an exception in manager %s get state. Exception: %s\n Traceback: %s\n", self._puid, ex, tb
            )


def manager_proc(
    pool_size: int, serialized_return_orc, serialized_main_orc, trace, args, manager_id, ser_pool_desc=None
):
    try:
        manager = Manager(pool_size, serialized_return_orc, serialized_main_orc, trace, args, manager_id, ser_pool_desc)
        manager.run()
        log.debug("Manager is exiting....")
    except Exception as ex:
        tb = traceback.format_exc()
        log.debug("There was an exception initing the manager: %s\n Traceback: %s", ex, tb)
        raise RuntimeError(f"There was an exception initing the manager: {ex}\n Traceback: {tb}")
