# Copyright (c) 2024, InfinityQ Technology, Inc.
from abc import abstractmethod, ABC
import numpy as np
import numpy.typing as npt

from ..numpy_util import convert_to_float32


class BaseConstraints(ABC):

    @abstractmethod
    def is_empty():
        """Return if all constraints are empty"""
        pass


    def _append_constraint(
        self,
        new_constraints: npt.NDArray[np.float32],
        existing_constraints: npt.NDArray[np.float32]
    ) -> npt.NDArray[np.float32]:
        """
        Appends new_constraints to existing_constraints and return the new formed one

        :param new_constraints: New constraint to append with the existing_constraints
        :param existing_constraints: Existing constraint that will be appended with

        :return: Existing constraint with the appeneded new constraints
        """
        # API only take float 32
        new_constraints = convert_to_float32(new_constraints)

        if existing_constraints is None:
            return new_constraints
        else:
            return np.append(existing_constraints, new_constraints, axis=0)


    def _rows_count(self, constraints: npt.NDArray[np.float32]) -> int:
        """
        :return: The number of constraints (rows) already set, 0 if never set
        """
        if constraints is None:
            return 0
        return constraints.shape[0]