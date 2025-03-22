# Copyright (c) 2025, InfinityQ Technology, Inc.

import io
from typing import Tuple

import numpy as np
from scipy.sparse import coo_array, save_npz

from titanq._model.array import ArrayLike


class ScipyCooArray(ArrayLike):

    def __init__(self, array: coo_array):
        """
        Creates a ScipyCooArray implementing ArrayLike

        :param array: The scipy COOrdinate array itself
        """
        self._array = array


    def array(self) -> coo_array:
        return self._array


    def shape(self) -> Tuple:
        return self.array().shape


    def np_type(self) -> np.dtype:
        return self.array().dtype


    def to_bytes(self) -> bytes:
        buffer = io.BytesIO()
        save_npz(buffer, self.array())
        return buffer.getvalue()