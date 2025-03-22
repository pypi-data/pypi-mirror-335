# Copyright (c) 2024, InfinityQ Technology, Inc.
from typing import Any, List, Tuple

from ..mps_parser import ColumnsType, MPSColumns


class SetOnceOrDefault:
    def __init__(
        self,
        default: Any,
        error_msg: str,
        allow_same_value: bool = False
    ) -> None:
        """
        SetOnceOrDefault creates an object with a default value that can only
        be set once. If not set, will use the default value.

        If allow_same_value is set to True, the object can be set again but has
        to be the exact same value.
        """
        self._default = default
        self._error_msg = error_msg
        self._allow_same_value = allow_same_value

        self._value = None

    def is_default(self) -> bool:
        """returns if the value is still at default state"""
        return self._value is None

    def set(self, value: Any):
        # a value has already been set
        if self._value is not None:
            # check if we allow the same value
            if self._allow_same_value and self._value == value:
                pass
            else:
                raise Exception(
                    f"{self._error_msg}: Tried to set twice a {self.__class__.__name__} " +
                    f"and had already the value '{self._value}' set, but tried to set it again with '{value}'")
        self._value = value

    def get(self) -> Any:
        return self._value if self._value is not None else self._default


def get_variables_and_types(mps_columns: List[MPSColumns]) -> List[Tuple[str, ColumnsType]]:
    """returns a list without duplicates but keeps an order"""
    variables_set = []
    seen = set()
    seen_add = seen.add # more efficient

    for column in mps_columns:
        if column.identifier() not in seen:
            seen_add(column.identifier())
            variables_set.append((column.identifier() ,column.type()))

    return variables_set
