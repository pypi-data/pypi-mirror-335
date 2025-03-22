# Copyright (c) 2025, InfinityQ Technology, Inc.

import io
from typing import Tuple

import numpy as np

from titanq._model.array import ArrayLike


class NumpyArray(ArrayLike):

    def __init__(self, array: np.ndarray):
        """
        Creates a NumpyArray implementing ArrayLike

        :param array: The numpy ndarray itself
        """
        self._array = array


    def array(self) -> np.ndarray:
        return self._array


    def shape(self) -> Tuple:
        return self.array().shape


    def np_type(self) -> np.dtype:
        return self.array().dtype


    def to_bytes(self) -> bytes:
        buffer = io.BytesIO()
        np.save(buffer, self.array())
        return buffer.getvalue()