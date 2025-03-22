# Copyright (c) 2024, InfinityQ Technology, Inc.
import enum
from typing import Optional, Tuple

import numpy as np

from titanq._model.array import ArrayLike


class Target(enum.Enum):
    """
    All target types currently supported by the solver
    """

    MINIMIZE = 'minimize'


class Objective:
    """
    Objective passed to TitanQ platform. It is consisted of the weight matrix and the bias vector.
    """

    def __init__(
        self,
        var_size: int,
        bias: ArrayLike,
        weights: Optional[ArrayLike],
        target: Target,
        constant_term: float
    ) -> None:
        if weights is not None:
            _verify_array(weights, "weights", expected_shape=(var_size, var_size), expected_type=np.float32)

        _verify_array(bias, "bias", expected_shape=(var_size, ), expected_type=np.float32)

        self._weights = weights
        self._bias = bias
        self._target = target
        self._constant_term = constant_term

    def bias(self) -> ArrayLike:
        """
        :return: The bias vector of this objective.
        """
        return self._bias

    def weights(self) -> Optional[ArrayLike]:
        """
        :return: The weights matrix of this objective.
        """
        return self._weights

    def target(self) -> Target:
        """
        :return: The Target for this objective.
        """
        return self._target

    def constant_term(self) -> float:
        """
        :return: The constant term (offset) for this objective
        """
        return self._constant_term


def _verify_array(array: ArrayLike, array_name: str, *, expected_shape: Tuple, expected_type: np.dtype):
    """
    Make sure the given array is the right shape and the right type.

    :param array: The array like to verify.
    :param array_name: the name of the array to be verified, use in error message.
    :param expected_shape: numpy compatible tuple of the expected shape.
    :param expected_type: expected numpy type for the array.

    :raise ValueError: if the array is not the right shape.
    :raise ValueError: if the value inside the array is not the right data type.
    """
    if array.shape() != expected_shape:
        raise ValueError(f"{array_name} shape {array.shape} does not fit the shape of the variable previously defined. Expected: {expected_shape}.")

    if array.np_type() != expected_type:
        raise ValueError(f"Unsupported {array_name} dtype ({array.np_type()}). Expected: {expected_type}.")
