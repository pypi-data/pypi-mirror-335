# Copyright (c) 2024, InfinityQ Technology, Inc.

from typing import Iterable, Tuple, Union

import numpy as np
from scipy.sparse import coo_array

CoordStoreType = Tuple[Tuple[int, int], Union[int, float]]


class CoordStore:
    """
    A simple and efficient coordinate store that allows adding or updating values
    at specific (x, y) coordinates.

    It uses a dictionary to store the coordinates, enabling O(1) lookup time for
    both updates and retrievals
    """

    def __init__(self, problem_size: int):
        """
        Initialize a CoordStore.

        :param size: A saved sized used to determine the total length of the storage, this
        is used for metadata only

        NOTE: The problem size does not have any correlation with the coordinates, append()
        method does not check if the coordinate is inside the size. It is simply used as a
        metadata for the class user.
        """
        self._problem_size = problem_size
        self._coords = {}


    def append(self, x: int, y: int, value: Union[int, float]) -> None:
        """Adds or update a value at the given (x, y) coordinate."""
        self._coords[(x, y)] = self._coords.get((x, y), 0) + value


    def problem_size(self) -> int:
        """Returns the problem size."""
        return self._problem_size


    def is_empty(self) -> bool:
        """Returns True if the the coordinate store is empty, otherwise False."""
        return not self._coords


    def __len__(self) -> int:
        """Returns the number of element in the store."""
        return len(self._coords)


    def __iter__(self) -> Iterable[CoordStoreType]:
        for key, value in self._coords.items():
            yield key, value


    def items(self) -> Iterable[CoordStoreType]:
        """Iterates over the coordinates with existing values."""
        return iter(self)


    def to_numpy_array(self) -> np.ndarray:
        """Converts into a dense numpy array."""
        array = np.zeros((self.problem_size(), self.problem_size()), dtype=np.float32)

        for (x, y), value in self.items():
            array[x, y] = value
        return array


    def to_coo_array(self) -> coo_array:
        """Converts into a sparse scipy COOrdinate matrix"""
        rows, cols = zip(*self._coords.keys())
        values = list(self._coords.values())

        return coo_array((values, (rows, cols)), shape=(self.problem_size(), self.problem_size()), dtype=np.float32)
