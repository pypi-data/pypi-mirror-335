# Copyright (c) 2024, InfinityQ Technology, Inc.
import enum
from typing import Any, List


class RowsType(str, enum.Enum):
    """
    All supported Rows type for .mps files in this parser
    """
    FREE_ROW = 'N'
    GREATER_OR_EQUAL = 'G'
    LOWER_OR_EQUAL = 'L'
    EQUALITY = 'E'


class ColumnsType(str, enum.Enum):
    """
    ALl supported Columns type for .mps files in this parser
    """
    CONTINUOUS = 'c'
    INTEGER = 'i'


class BoundsType(str, enum.Enum):
    """
    All supported Bounds type for .mps files in this parser
    """
    LOWER_BOUND = 'LO'
    LOWER_BOUND_INT = 'LI'
    UPPER_BOUND = 'UP'
    UPPER_BOUND_INT = 'UI'
    FIXED_VALUE = 'FX'
    FREE_VARIABLE = 'FR'
    MINUS_INFINITY = 'MI'
    PLUS_INFINITY = 'PL'
    BINARY_VARIABLE = 'BV'
    SEMI_CONTINUOUS = 'SC'

    @classmethod
    def needs_value(cls) -> List['BoundsType']:
        """returns a list of the bounds type that needs a value assigned to them"""
        return [cls.LOWER_BOUND, cls.LOWER_BOUND_INT, cls.UPPER_BOUND, cls.UPPER_BOUND_INT, cls.FIXED_VALUE]


class SectionType(str, enum.Enum):
    """
    All supported Sections type for .mps files in this parser
    """
    NAME = "NAME"
    ROWS = "ROWS"
    COLUMNS = "COLUMNS"
    RHS = "RHS"
    RANGES = "RANGES"
    BOUNDS = "BOUNDS"
    QUADOBJ = "QUADOBJ"
    QMATRIX = "QMATRIX"
    ENDATA = "ENDATA"


class UniqueList:
    def __init__(
        self,
        error_msg: str
    ) -> None:
        """
        Unique list is an iterable containing a list that can only have unique values.
        """
        self._list = []
        self._set = set()
        self._error_msg = error_msg

    def append(self, value: Any) -> None:
        if value in self._set:
            raise Exception(
                f"{self._error_msg}: Tried to append an already existing value in a {self.__class__.__name__} '{value}'")
        self._list.append(value)
        self._set.add(value)

    def __iter__(self):
        return iter(self._list)