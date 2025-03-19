# Copyright (c) 2024, InfinityQ Technology, Inc.
import logging
from typing import Any, Optional
import numpy as np
import numpy.typing as npt

from .base_constraints import BaseConstraints
from ...errors import ConstraintSizeError

log = logging.getLogger("TitanQ")


class QuadConstraints(BaseConstraints):
    def __init__(self) -> None:
        self._quad_constraint_weights = None
        self._quad_constraint_bounds = None
        self._quad_constraint_linear_weights = None


    def is_empty(self) -> bool:
        """return if all constraints are empty"""
        return (
            self._quad_constraint_weights is None and
            self._quad_constraint_bounds is None and
            self._quad_constraint_linear_weights is None
        )


    def add_constraint(
        self,
        num_variables: int,
        quad_constraint_weights: npt.NDArray[Any],
        quad_constraint_bounds: npt.NDArray[Any],
        quad_constraint_linear_weights: Optional[npt.NDArray[Any]] = None
    ) -> None:
        """
        Add a quadratic constraint to the existing ones

        :param num_variables: the number of variables from the model
        :param quad_constraint_weights: quadratic constraint weights to append to the existing ones.
        :param quad_constraint_bounds: quadratic constraint bounds to append to the existing ones.
        :param quad_constraint_linear_weights: quadratic constraint linear weights to append to the existing ones.

        :raises ConstraintSizeError:
            Number of constraints is different than the number of
            variables.
        """
        # shape validation
        if quad_constraint_weights.shape != (num_variables, num_variables):
            raise ConstraintSizeError(
                "Invalid constraint_mask shape: expected (N,N) where N is the number of variables "
                + f"({num_variables},{num_variables}), but got {quad_constraint_weights.shape}.")

        if quad_constraint_linear_weights is not None and quad_constraint_linear_weights.shape != (1, num_variables):
                raise ValueError(
                    "Invalid constraint_linear_weights shape: expected (N,) where N is "
                    + f"the number of variables ({num_variables}), "
                    + f"but got {quad_constraint_linear_weights.shape}.")

        self._quad_constraint_weights = self._append_constraint(quad_constraint_weights, self._quad_constraint_weights)
        self._quad_constraint_bounds = self._append_constraint(quad_constraint_bounds, self._quad_constraint_bounds)

        if quad_constraint_linear_weights is not None:
            self._quad_constraint_linear_weights = self._append_constraint(
                quad_constraint_linear_weights,
                self._quad_constraint_linear_weights)


    def weights(self) -> Optional[npt.NDArray[np.float32]]:
        """
        :return: The quadratic weights constraints.
        """
        return self._quad_constraint_weights


    def bounds(self) -> Optional[npt.NDArray[np.float32]]:
        """
        :return: The quadratic bounds constraints.
        """
        return self._quad_constraint_bounds

    def linear_weights(self) -> Optional[npt.NDArray[np.float32]]:
        """
        :return: The quadratic linear weights constraints.
        """
        return self._quad_constraint_linear_weights
