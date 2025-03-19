# Copyright (c) 2025, InfinityQ Technology, Inc.

from typing import Optional

import numpy as np
from scipy.sparse import coo_array

from titanq._model.array import Array, ArrayLike
from titanq._model.array.numpy_array import NumpyArray
from titanq._model.array.scipy_coo_array import ScipyCooArray


class ArrayLikeFactory:
    """
    Factory class for the array like type.

    `create()` simply creates an ArrayLike based on the instance type
    """

    def create(self, array: Optional[Array]) -> Optional[ArrayLike]:
        """ returns the corresponding ArrayLike based on the instance type """
        if array is None:
            return None

        if isinstance(array, np.ndarray):
            return NumpyArray(array)
        elif isinstance(array, coo_array):
            return ScipyCooArray(array)
        else:
            raise ValueError(f"Unsupported array type: {type(array)}")
