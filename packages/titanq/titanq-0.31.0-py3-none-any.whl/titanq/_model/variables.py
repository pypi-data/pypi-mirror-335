# Copyright (c) 2024, InfinityQ Technology, Inc.

from abc import ABC, abstractmethod
import enum
from typing import Tuple

import numpy.typing as np_type
import numpy as np
import symengine as se
import symengine.lib.symengine_wrapper as se_type

class Vtype(str, enum.Enum):
    """
    All variable types currently supported by the solver.

    ℹ️ **NOTE:** Bipolar variables are not directly supported,
    but :class:`tools.BipolarToBinary` can be used as an alternative.
    """

    BINARY = 'binary'
    INTEGER = 'integer'
    CONTINUOUS = 'continuous'

    def __str__(self) -> str:
        return str(self.value)

    def _api_str(self) -> str:
        """
        Convert the `Vtype` enum to its corresponding API string representation.

        This method returns a shorthand character used by the API to identify 
        the variable type. The mapping is as follows:

        - 'b' for BINARY
        - 'c' for CONTINUOUS
        - 'i' for INTEGER

        Returns
        -------
        A string representing the variable type in the API.
        """
        if self == Vtype.BINARY:
            return 'b'
        elif self == Vtype.CONTINUOUS:
            return 'c'
        else: # Vtype.Integer
            return 'i'


class Variable(ABC, se_type.Symbol):
    def __init__(self, parent_name: str, parent_index: int, problem_index: int,  *args, **kwargs):
        name = f"{parent_name}[{parent_index}]"
        super().__init__(name, *args, **kwargs)

        self._problem_index = problem_index
        self._parent_name = parent_name

    @abstractmethod
    def vtype(self) -> Vtype:
        """
        Returns
        -------
        Type of the variable.
        """

    @abstractmethod
    def variable_bounds(self) -> np_type.NDArray[np.float32]:
        """
        Returns
        -------
        The variable bounds associated to this variable
        """

    def problem_index(self) -> int:
        """
        Returns
        -------
        The index of this variable for the whole problem
        """
        return self._problem_index

    def parent_name(self) -> str:
        """
        Returns
        -------
        The name of the parent variable vector
        """
        return self._parent_name


class BinaryVariable(Variable):
    def vtype(self) -> Vtype:
        return Vtype.BINARY

    def variable_bounds(self) -> np_type.NDArray[np.float32]:
        return np.array([0,1], dtype=np.float32)


class IntegerVariable(Variable):
    def __init__(self, parent: str, index: int, problem_index: int, bounds: Tuple[int, int]) -> None:
        super().__init__(parent, index, problem_index)
        self._bounds = bounds

    def vtype(self) -> Vtype:
        return Vtype.INTEGER

    def variable_bounds(self) -> np_type.NDArray[np.float32]:
        return self._bounds

class ContinuousVariable(Variable):
    def __init__(self, parent: str, index: int, problem_index: int, bounds: Tuple[int, int]) -> None:
        super().__init__(parent, index, problem_index)
        self._bounds = bounds

    def vtype(self) -> Vtype:
        return Vtype.CONTINUOUS

    def variable_bounds(self) -> np_type.NDArray[np.float32]:
        return self._bounds