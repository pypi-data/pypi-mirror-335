# Copyright (c) 2024, InfinityQ Technology, Inc.
from typing import Tuple
import numpy as np
from warnings import warn

from ...._model.model import Model, Vtype

from .utils import SetOnceOrDefault


class VariableBounds:
    def __init__(self, def_lower: float, def_upper: float, def_vtype: Vtype) -> None:
        """
        helper class that intialize a variable bounds with some default values and all
        of these values can only be set one
        """
        self._lower = SetOnceOrDefault(def_lower, error_msg="Variable with more than one lower bound")
        self._upper = SetOnceOrDefault(def_upper, error_msg="Variable with more than one upper bound")
        self._vtype = SetOnceOrDefault(def_vtype, allow_same_value=True, error_msg="Variable with more than one type")

    def set(self, lower: float = None, upper: float = None, vtype: Vtype = None) -> None:
        if lower is not None:
            self._lower.set(lower)

        if upper is not None:
            self._upper.set(upper)
            # if the upperbound is set to something less than 0
            if upper < 0 and self._lower.is_default():
                self._lower.set(-np.nan)
                warn(f"Found an upper bound lower than 0: '{upper}', the lower bound was set to '-np.nan'")

        if vtype is not None:
            self._vtype.set(vtype)


    def is_binary(self) -> bool:
        """ return if the variable type has been defined as a binary """
        return self._vtype.get() == Vtype.BINARY


    def into_model_variable(
        self,
        model: Model,
        name: str,
        variable_is_integer: bool,
    ) -> None:
        """vtype is optional here, it will be considered only if applied"""
        # if the variable was overriden and no bounds were set
        # we assume the bounds as 0 (zero) and 1 (one)
        if variable_is_integer and self._lower.is_default() and self._upper.is_default():
            variable_bounds = [[0.0, 1]]
        else:
            variable_bounds=[[self._lower.get(), self._upper.get()]] if self._vtype.get() is not Vtype.BINARY else None

        model.add_variable_vector(
            name=name,
            size=1,
            vtype=Vtype.INTEGER if variable_is_integer else self._vtype.get(),
            variable_bounds=variable_bounds
        )


class ConstraintBounds:
    def __init__(self, def_lower: float, def_upper: float) -> None:
        """
        helper class that intialize a constraint bounds with some default values and all
        of these values can only be set one
        """
        self._lower = SetOnceOrDefault(def_lower, error_msg="Constraint with more than one lower bound")
        self._upper = SetOnceOrDefault(def_upper, error_msg="Constraint with more than one upper bound")

    def set(self, lower: float = None, upper: float = None, vtype: Vtype = None):
        if lower is not None:
            self._lower.set(lower)

        if upper is not None:
            self._upper.set(upper)

    def get(self) -> Tuple[float, float]:
        return (self._lower.get(), self._upper.get())