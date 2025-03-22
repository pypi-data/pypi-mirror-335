# Copyright (c) 2025, InfinityQ Technology, Inc.

"""
Array Transform module

This module provides functionality for checking various types of arrays and transform them in need.
It transforms them into different formats based on the chosen strategy.

It utilizes the strategy pattern, to provide a flexible approach for handling different array formats
and different check logic.

Example Usage
-------------

    # choose the strategy
    a_strategy = AStrategy()

    # create the transform checker with the strategy
    array_checker = ArrayTransformChecker(AStrategy)

    # create the array
    array = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 0]])

    # use the transform checker
    result_array = array_checker.check_and_transform(array)
"""

from abc import ABC, abstractmethod
from typing import Union

from titanq._model.array import Array
from titanq._model.coord_store import CoordStore


# accepted arrays and what the the module can output
StrategyInputArrays = Union[Array, CoordStore]
StrategyOutputArrays = Array


class ArrayTransformStrategy(ABC):
    """
    Abstract class that each strategy would implement.
    """

    @abstractmethod
    def check_and_transform(self, array: StrategyInputArrays) -> StrategyOutputArrays:
        """
        Checks the array and transform if needed. It can output the same array as the input.

        :param array: The array to check and transform if needed

        :returns: The transformed array depending on the chosen strategy
        """
        pass


class ArrayTransformChecker:
    """
    Array transform checker class that would apply a given strategy.

    You can apply the strategy at the creation time or by calling `set_strategy()`.
    """

    def __init__(self, strategy: ArrayTransformStrategy):
        self._strategy = strategy

    def check_and_transform(self, array: StrategyInputArrays) -> StrategyOutputArrays:
        return self._strategy.check_and_transform(array)