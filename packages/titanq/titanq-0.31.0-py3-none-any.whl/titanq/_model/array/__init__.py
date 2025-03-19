# Copyright (c) 2025, InfinityQ Technology, Inc.

"""
This module defines an abstract base class, ArrayLike, which serves as an interface for objects that are
"array-like" in nature. The goal of this interface is to provide a set of methods that any class whether
it's a numpy.ndarray or any other specialized one (scipy's coo_array), can implement to ensure the
compatibility with certain behaviours expected for the SDK.
"""

from abc import ABC, abstractmethod
from typing import Any, Tuple, Union

import numpy as np
from scipy.sparse import coo_array


# Alias for the supported array types in the TitanQ SDK
Array = Union[np.ndarray, coo_array]


class ArrayLike(ABC):
    """
    This class represents an array like passed in by a user. We support different formats (e.g. sparse, dense),
    so this class will hide the specific format and allow different array formats to behave the same.
    """

    @abstractmethod
    def array(self) -> Any:
        """ returns the instance itself of the array like """
        pass

    @abstractmethod
    def shape(self) -> Tuple:
        """ returns the shape of the array like """
        pass


    @abstractmethod
    def np_type(self) -> np.dtype:
        """ returns the type of the array like in a np.dtype format """
        pass


    @abstractmethod
    def to_bytes(self) -> bytes:
        """ returns the np type array as bytes """
        pass
