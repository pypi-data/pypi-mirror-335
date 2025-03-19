# Copyright (c) 2024, InfinityQ Technology, Inc.
from .model import Model
from .objective import Target
from .optimize_response import OptimizeResponse
from .variables import Vtype
from .precision import Precision

# constraints folder
from .constraints import Constraints, QuadConstraints


# keep fast_sum and fastSum for retro compatibility. mark them as deprecated
from deprecated import deprecated

@deprecated(reason="use Python's built-in sum function instead")
def fast_sum(*args, **kwargs):
    return sum(*args, **kwargs)

@deprecated(reason="use Python's built-in sum function instead")
def fastSum(*args, **kwargs):
    return sum(*args, **kwargs)