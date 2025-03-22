# Copyright (c) 2024, InfinityQ Technology, Inc.

from typing import List
from titanq._model.constraints.constraint_type import ConstraintType


class Manifest:
    """
    A manifest object to keep track of some data/information about the shape or the type
    that can be useful for the TitanQ API (input --> manifest).

    Currently it only holds constraint types information. Some flags will be raised in the
    manifest depending on which type of constraints are included in the request.
    """

    def __init__(self) -> None:
        self._constraints_type: List[ConstraintType] = []

    def add_constraint_type(self, constraint_type: ConstraintType) -> None:
        """ Declares the passed 'constraint_type' is being used. """
        if constraint_type is None:
            raise TypeError("Got a 'constraint_type' of type None")

        self._constraints_type.append(constraint_type)

    def has_set_partitioning_constraint(self) -> bool:
        """
        :return: if the manifest has set partitioning constraint.
        """
        return ConstraintType.SET_PARTITIONING in self._constraints_type

    def has_cardinality_constraint(self) -> bool:
        """
        :return: if the manifest has cardinality constraint.
        """
        return ConstraintType.CARDINALITY in self._constraints_type

    def has_equality_constraint(self) -> bool:
        """
        :return: if the manifest has equality constraint.
        """
        return ConstraintType.EQUALITY in self._constraints_type

    def has_inequality_constraint(self) -> bool:
        """
        :return: if the manifest has inequality constraint.
        """
        return ConstraintType.INEQUALITY in self._constraints_type
