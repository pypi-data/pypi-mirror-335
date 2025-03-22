# Copyright (c) 2024, InfinityQ Technology, Inc.
from typing import List, Optional
from warnings import warn

from titanq.errors import MpsMissingValueError
from .utils import BoundsType, ColumnsType, RowsType
from ._visitor import LineSection, Visitor


class MPSName(LineSection):
    def __init__(self, name: str) -> None:
        self._name = name

    def name(self) -> str: return self._name

    def _accept(self, visitor: Visitor):
        visitor._visit_name(self)

    def __str__(self):
        """.mps format"""
        return self._name


class MPSRow(LineSection):
    """MPS Row section handler"""
    def __init__(self, sense: RowsType, identifier: str) -> None:
        self._sense = sense
        self._identifier = identifier

    def sense(self) -> RowsType: return self._sense
    def identifier(self) -> str: return self._identifier

    def _accept(self, visitor: Visitor):
        if self._sense == RowsType.FREE_ROW:
            visitor._visit_free_row(self)
        else:
            visitor._visit_rows(self)

    def __str__(self):
        """.mps format"""
        return f"{self._sense}\t{self._identifier}"

class MPSColumns(LineSection):
    def __init__(self, identifier: str,row_identifier: str, coeff: float, type: ColumnsType) -> None:
        self._identifier = identifier
        self._row_identifier = row_identifier
        self._coeff = coeff
        self._type = type

    def identifier(self) -> str: return self._identifier
    def row_identifier(self) -> str: return self._row_identifier
    def coeff(self) -> float: return self._coeff
    def type(self) -> ColumnsType: return self._type

    def _accept(self, visitor: Visitor):
        visitor._visit_columns(self)

    def __str__(self):
        """.mps format"""
        return f"\t{self._identifier}\t{self._row_identifier}\t{self._coeff}"


class MPSRhs(LineSection):
    def __init__(self, identifier: str, row_identifier: str, coeff: float) -> None:
        self._identifier = identifier
        self._row_identifier = row_identifier
        self._coeff = coeff

    def identifier(self) -> str: return self._identifier
    def row_identifier(self) -> str: return self._row_identifier
    def coeff(self) -> float: return self._coeff

    def _accept(self, visitor: Visitor):
        visitor._visit_rhs(self)

    def __str__(self):
        return f"\t{self._identifier}\t{self._row_identifier}\t{self._coeff}"

class MPSRanges(LineSection):
    def __init__(self, identifier: str, row_identifier: str, coeff: float) -> None:
        self._identifier = identifier
        self._row_identifier = row_identifier
        self._coeff = coeff

    def identifier(self) -> str: return self._identifier
    def row_identifier(self) -> str: return self._row_identifier
    def coeff(self) -> float: return self._coeff

    def _accept(self, visitor: Visitor):
        visitor._visit_ranges(self)

    def __str__(self):
        """.mps format"""
        return f"\t{self._identifier}\t{self._row_identifier}\t{self._coeff}"


class MPSBounds(LineSection):
    def __init__(self, identifier: str, type: BoundsType, column_identifier: str, value: Optional[float] = None) -> None:
        self._identifier = identifier
        self._type = type
        self._column_identifier = column_identifier
        self._value = value

        # check for mandatory values in some type of bounds
        if self._type in BoundsType.needs_value():
            if self._value is None:
                raise MpsMissingValueError(
                    f"No value was assigned for a bound of type '{self._type}', "
                    f"with the identifier '{self._identifier}'")
        else:
            # a value assigned to a type that does not require one
            if self._value is not None:
                warn(f"A value was assigned for a bound of type '{self._type}', with the identifier '{self._identifier}', "
                      "but this one does not require any value, the value will be ignored instead")

    def identifier(self) -> str: return self._identifier
    def type(self) -> BoundsType: return self._type
    def column_identifier(self) -> str: return self._column_identifier
    def value(self) -> Optional[float]: return self._value

    def _accept(self, visitor: Visitor):
        visitor._visit_bounds(self)

    def __str__(self):
        """.mps format"""
        return f"{self._type}\t{self._identifier}\t{self._column_identifier}\t{self._value}"


class MPSQuadobj(LineSection):
    def __init__(self, row_identifier: str, column_identifier: str, value: float) -> None:
        self._row_identifier = row_identifier
        self._column_identifier = column_identifier
        self._value = value

    def row_identifier(self) -> str: return self._row_identifier
    def column_identifier(self) -> str: return self._column_identifier
    def value(self) -> float: return self._value

    def _accept(self, visitor: Visitor):
        visitor._visit_quadobj(self)

    def __str__(self):
        """.mps format"""
        return f"{self._row_identifier}\t{self._column_identifier}\t{self._value}"

class MPSEndata(LineSection):
    def _accept(self, visitor: Visitor):
        visitor._visit_endata()


# Main MPS object containing all info
class MPSObject(Visitor):

    def __init__(self) -> None:
        self.name: str = None
        self.free_row: MPSRow = None # called as free row, which is the objective row
        self.objective_offset: Optional[MPSRhs] = None
        self.rows: List[MPSRow] = []
        self.columns: List[MPSColumns] = []
        self.rhs: List[MPSRhs] = []
        self.ranges: List[MPSRanges] = []
        self.bounds: List[MPSBounds] = []
        self.quadobj: List[MPSQuadobj] = []
        self.endata: bool = False

    # visitor methods
    def _visit_name(self, name: MPSName): self.name = name.name()
    def _visit_rows(self, row: MPSRow): self.rows.append(row)
    def _visit_columns(self, column: MPSColumns): self.columns.append(column)
    def _visit_rhs(self, rhs: MPSRhs): self.rhs.append(rhs)
    def _visit_ranges(self, range: MPSRanges): self.ranges.append(range)
    def _visit_bounds(self, bound: MPSBounds): self.bounds.append(bound)
    def _visit_quadobj(self, quadobj: MPSQuadobj): self.quadobj.append(quadobj)
    def _visit_endata(self): self.endata = True
    def _visit_free_row(self, row: MPSRow):
        # more than one free row was specified
        if self.free_row is not None:
            warn(
                f"Found a free row {RowsType.FREE_ROW} identified as '{row.identifier()}', "
                f"but one was already identified with: '{self.free_row.identifier()}'. Ignoring the new one"
            )
        else:
            self.free_row = row