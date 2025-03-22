# Copyright (c) 2025, InfinityQ Technology, Inc.

"""
The sparse threshold strategy allows to convert the arrays into others depending on a threshold.

This can help optimizing the chosen array, by helping the end-user to obtain much faster results by
opting for sparse arrays, or even by reducing his total RAM Usage.
"""

import numpy as np
from scipy.sparse import coo_array

from titanq._model.coord_store import CoordStore
from titanq._model.transform import (
    ArrayTransformStrategy,
    StrategyInputArrays,
    StrategyOutputArrays
)


_SPARSE_THRESHOLD = 0.2 # 20%


class SparseThresholdStrategy(ArrayTransformStrategy):
    """
    This strategy bases on the sparse threshold, meaning if the calculated density
    is abover certain threshold, the array would transform to another one.
    """

    def check_and_transform(self, array: StrategyInputArrays) -> StrategyOutputArrays:
        array_type_dispatcher = {
            CoordStore: self._handle_coordstore,
            coo_array: self._handle_coo_array,
            np.ndarray: self._handle_ndarray
        }

        handler = array_type_dispatcher.get(type(array))
        if handler:
            return handler(array)
        else:
            raise ValueError(f"Unsupported array type for the sparse threshold check: {type(array)}")


    def _handle_coordstore(self, array: CoordStore) -> StrategyOutputArrays:
        density = (len(array) + 1) / (array.problem_size() * array.problem_size())

        if density > _SPARSE_THRESHOLD:
            return array.to_numpy_array()
        else:
            return array.to_coo_array()


    def _handle_coo_array(self, array: coo_array) -> StrategyOutputArrays:
        density = array.nnz / array.shape[0] * array.shape[1]

        if density > _SPARSE_THRESHOLD:
            raise NotImplementedError("Sparse threshold strategy does not support yet conversion from coo_array to numpy arrays.")
        else:
            return array # do nothing


    def _handle_ndarray(self, array: np.ndarray) -> StrategyOutputArrays:
        density = np.count_nonzero(array) / array.size
        if density > _SPARSE_THRESHOLD:
            return array # do nothing
        else:
            return NotImplementedError("Sparse threshold strategy does not support yet conversion from numpy arrays to coo_array.")