import os
import enum
from dataclasses import dataclass, field, fields
import threading
import json

from dragon.infrastructure import facts as dfacts
from typing import Dict


@dataclass
class Policy:
    """
    The purpose of the Policy object is to enable fine-tuning of process distribution
    across nodes, devices, cores, and etc.
    For example spawning a process that should only run on certain CPU cores, or only have
    access to specific GPU devices on a node, or how to spread a collection of processes
    over nodes (e.g. Round-robin, Blocking, etc).

    There is a default global Policy in place that utilizes no core or accelerator affinity,
    and places processes across nodes in a round-robin fashion.  Using Policy is meant to fine-tune
    this default policy, and any non-specific attributes will use the default policy values.

    For a full example of setup for launching processes through Global Services, see `examples/dragon_gs_client/pi_demo.py`
    When launching a process simply create a policy with the desired fine-tuning, and pass it in as a paramter.

    .. code-block:: python

        import dragon.globalservices.process as dgprocess
        import dragon.infrastructure.policy as dgpol

        # Do setup
        # ...
        # ...
        # Create a custom process for core affinity and selecting a specific GPU
        policy = dgpol.Policy(cpu_affinity=[0,2], gpu_affinity=[0])
        # Launch the process with the fine-tuned policy
        p = dgprocess.create(cmd, wdir, cmd_params, None, options=options, policy=policy)
    """

    class Placement(enum.IntEnum):
        """
        Which node to assign a policy to.

        Local and Anywhere will be useful later for multi-system communication
        Right now Placement will have little effect unless HOST_NAME or HOST_ID
        are used, which will try to place a policy on the specified node

        LOCAL - Local to current system of nodes
        ANYWHERE - Place anywhere
        HOST_NAME - Place on node with specific name
        HOST_ID - Place on node with specific ID
        DEFAULT - Defaults to ANYWHERE
        """

        LOCAL = -5  # Local to the current system of nodes
        ANYWHERE = -4  # What it says on the tin
        HOST_NAME = -3  # Tells evaluator to check host_name in policy and apply to that node
        HOST_ID = -2  # Tells evaluator to check host_id in policy and apply to that node
        DEFAULT = -1  # For now, defaults to ANYWHERE

    class Distribution(enum.IntEnum):
        """
        Pattern to use to distribute policies across nodes

        ROUNDROBIN
        BLOCK
        DEFAULT - Defaults to roundrobin
        """

        ROUNDROBIN = enum.auto()
        BLOCK = enum.auto()
        DEFAULT = enum.auto()

    # TODO: Not implemented
    class WaitMode(enum.IntEnum):
        """Channel WaitMode type"""

        IDLE = enum.auto()
        SPIN = enum.auto()
        DEFAULT = enum.auto()

    placement: Placement = Placement.DEFAULT
    host_name: str = ""  # To be populated by caller in use with Placement.HOST_NAME
    host_id: int = -1  # To be populated by caller in use with Placement.HOST_ID
    distribution: Distribution = Distribution.DEFAULT
    cpu_affinity: list[int] = field(
        default_factory=list
    )  # To be populated by called in use with Affinity.SPECIFIC, specify exact device IDs or cores
    gpu_env_str: str = ""  # To be used with gpu_affinity for vendor specific environment vars
    gpu_affinity: list[int] = field(default_factory=list)
    wait_mode: WaitMode = WaitMode.DEFAULT  # TODO (For channels)
    refcounted: bool = True  # TODO (Apply refcounting for this resource)

    def __post_init__(self):
        if isinstance(self.placement, int):
            self.placement = Policy.Placement(self.placement)
        if isinstance(self.distribution, int):
            self.distribution = Policy.Distribution(self.distribution)
        if isinstance(self.WaitMode, int):
            self.wait_mode = Policy.WaitMode(self.wait_mode)

    @property
    def sdesc(self) -> Dict:
        return self.get_sdict()

    def get_sdict(self) -> Dict:
        rv = {
            "placement": self.placement,
            "host_name": self.host_name,
            "host_id": self.host_id,
            "distribution": self.distribution,
            "cpu_affinity": self.cpu_affinity,
            "gpu_env_str": self.gpu_env_str,
            "gpu_affinity": self.gpu_affinity,
            "wait_mode": self.wait_mode,
            "refcounted": self.refcounted,
        }

        return rv

    @classmethod
    def from_sdict(cls, sdict):
        return Policy(**sdict)

    @classmethod
    def _init_thread_policy(cls):
        # This is put in thread-local storage to insure that it behaves in a
        # multi-threaded environment.
        if not hasattr(_policy_local, "policy_stack"):
            # start with an empty list.
            _policy_local.policy_stack = []
            try:
                policy_env = os.environ[dfacts.DRAGON_POLICY_CONTEXT_ENV]
                policy_sdesc = json.loads(policy_env)
                _policy_local.policy_stack.append(Policy.from_sdict(policy_sdesc))
            except (KeyError, json.JSONDecodeError):
                pass

    @classmethod
    def thread_policy(cls):
        return_val = cls()
        cls._init_thread_policy()

        # The following merges the policy stack, returning a policy that
        # reflects the aggregate policy defined by the stack.
        if _policy_local.policy_stack:

            # Iterate backwards through the policy stack, merging each
            # sucessive policy into our aggregate return value
            for i in range(-1, -len(_policy_local.policy_stack) - 1, -1):
                return_val = Policy.merge(_policy_local.policy_stack[i], return_val)

        return cls.from_sdict(return_val.get_sdict())

    def __enter__(self):
        self._init_thread_policy()
        _policy_local.policy_stack.append(self)

    def __exit__(self, *args):
        _policy_local.policy_stack.pop()

    @classmethod
    def merge(cls, low_policy, high_policy):
        """
        Merge two policies, using values from high_policy for values not assigned on init
        Returns a new policy

        :param low_policy: Default values will be replaced by `high_policy` values
        :type low_policy: Policy
        :param high_policy: Non-default values take precedence
        :type high_policy: Policy
        :return: Merged policy object
        :rtype: Policy
        """

        retain = {}

        for f in fields(high_policy):
            v = getattr(high_policy, f.name)

            # if the value is a Default value, do not retain
            if v == f.default:
                continue

            # Lists use default_factory to create a new instance, so checking f.default doesn't work.
            # If the list 'v' is empty (as in 'not v'), do not retain.
            if isinstance(v, list) and not v:
                continue

            retain[f.name] = v  # Value was assigned specifically, retain

        kwargs = {**low_policy.get_sdict(), **retain}  # Merge retained policy values with high priority values
        return cls(**kwargs)

    @classmethod
    def global_policy(cls):
        return cls.from_sdict(GS_GLOBAL_POLICY_SDICT)


# Global policy to merge incoming policies against
GS_GLOBAL_POLICY_SDICT = {
    "placement": Policy.Placement.ANYWHERE,
    "distribution": Policy.Distribution.ROUNDROBIN,
    "wait_mode": Policy.WaitMode.IDLE,
}

# _policy_local is private to the current thread
_policy_local = threading.local()
