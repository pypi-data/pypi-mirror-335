# Copyright (c) 2024, InfinityQ Technology, Inc.
import abc
from warnings import warn
from pyparsing import LineEnd, Opt, Optional, Or, ParseException, ParserElement, alphanums, nums, Group, OneOrMore, Word, printables
from typing import List, Union

from titanq.errors import MpsMalformedFileError, MpsMissingValueError

from .model import (
    MPSBounds,
    MPSColumns,
    MPSEndata,
    MPSName,
    MPSQuadobj,
    MPSRanges,
    MPSRhs,
    MPSRow,
)
from .utils import BoundsType, ColumnsType, RowsType, SectionType, UniqueList
from ._visitor import LineSection


# Following this IBM documentation, this parser currently uses spaces as delimiters
# https://www.ibm.com/docs/en/icos/22.1.0?topic=standard-records-in-mps-format

# For integer variables both ways are supported (COLUMNS via markers and in the bounds section)
# https://www.ibm.com/docs/en/icos/22.1.1?topic=extensions-integer-variables-in-mps-files

# mps char limits
_MAX_IDENTIFIER_LENGTH = 255
_MAX_NUMERIC_LENGTH = 25

# Integer variables markers in COLUMNS
_INTEGER_MARKER = "'MARKER'" # 'MARKER'
_INTEGER_START = "'INTORG'" # 'INTORG'
_INTEGER_END = "'INTEND'" # 'INTEND'

_MPS_FILE_DEFAULT_NAME = "IMPORTED_BY_TITANQ"

# Pyparser grammar
number = Word(nums + "-.", max=_MAX_NUMERIC_LENGTH) # numbers can have decimals and can be negative
rows_type = Or([type.value for type in RowsType])
bounds_type = Or([type.value for type in BoundsType])
identifier = Word(alphanums + "_[]", max=_MAX_IDENTIFIER_LENGTH)


def _parse_with_error_handling(element: ParserElement, line: str, line_index: str):
    """ Wrap ParseException with MPSMalformedFileError"""
    try:
        return element.parseString(line)
    except ParseException as ex:
        # As an example, this should read as:
        # "Expected {'N' ^ 'G' ^ 'L' ^ 'E'}, found 'AG  ROW01' (line: 4)"
        raise MpsMalformedFileError(f"{ex.msg}, found '{ex.pstr}' (line: {line_index})")


class SectionParser(abc.ABC):
    """class interface for any section needed to be parsed"""
    def __init__(self, start_index: int, lines: List[str]) -> None:
        super().__init__()
        self._start_index = start_index
        self._lines = lines

    def parse() -> List[LineSection]:
        """parse the given lines"""


class NameParser(SectionParser):
    """parses the NAME section of an .mps file into python objects"""

    def parse(self) -> List[MPSName]:
        # possible format 1 --> ['NAME', 'TITANQ-1-Project-50%']
        # possible format 2 --> ['NAME']
        if len(self._lines) > 1:
            raise MpsMalformedFileError(f"Found more than 2 lines for section '{SectionType.NAME}'")

        element = SectionType.NAME.value + Optional(Word(printables, max=_MAX_IDENTIFIER_LENGTH)) + LineEnd()
        parsed_elements = element.parseString(self._lines[0])

        # give it a default name if nothing was set
        name = parsed_elements[1] if len(parsed_elements) > 1 else _MPS_FILE_DEFAULT_NAME
        return [MPSName(name=name)]


class RowsParser(SectionParser):
    """parses the ROWS section of an .mps file into python objects"""

    def __init__(self, start_index: int, lines: List[str]) -> None:
        super().__init__(start_index, lines)
        self._rows_identifier = UniqueList(f"Found duplicates in the '{SectionType.ROWS}' section")
        self._free_row = None


    def _set_free_row(self, free_row_identifier):
        if self._free_row is not None:
            warn(
                f"Found a free row {RowsType.FREE_ROW} identified as '{free_row_identifier}', "
                f"but one was already identified with: '{self._free_row}'. New one will be ignored"
            )
        self._free_row = free_row_identifier


    def parse(self) -> List[MPSRow]:
        # possible format --> ['N', 'OBJ']
        rows = []
        for index, line in enumerate(self._lines):
            element = rows_type + identifier + LineEnd()
            parsed_elements = _parse_with_error_handling(element, line, self._start_index + index)

            row_identifier = parsed_elements[1]
            sense = RowsType(parsed_elements[0])
            if sense == RowsType.FREE_ROW:
                self._set_free_row(row_identifier)

            rows.append(MPSRow(sense=sense, identifier=row_identifier))

        if self._free_row is None:
            raise MpsMissingValueError(f"Did not find a free row '{RowsType.FREE_ROW}' in the '{SectionType.ROWS}' section")

        return rows


class ColumnParser(SectionParser):
    """parses the COLUMNS section of an .mps file into python objects"""

    def __init__(self, start_index: int, lines: List[str]) -> None:
        super().__init__(start_index, lines)
        self._type = ColumnsType.CONTINUOUS


    def _activate_integer_mode(self): self._type = ColumnsType.INTEGER
    def _deactivate_integer_mode(self): self._type = ColumnsType.CONTINUOUS


    def _handle_marker_line(self, value: str) -> None:
        if value == _INTEGER_START:
            self._activate_integer_mode()
        elif value == _INTEGER_END:
            self._deactivate_integer_mode()


    def parse(self) -> List[MPSColumns]:
        # possible format 1 --> ['C1', ['R1', '2.0']]
        # possible format 2 --> ['C2', ['R2', '-2.0'], ['R3', '-1.0]]
        # possible format 3 --> ['MARK', 'MARKER, 'INTORG']
        # possible format 4 --> ['SOMENAME', 'MARKER, 'INTEND']
        columns = []
        for index, line in enumerate(self._lines):
            row_element = Group(Or([identifier, _INTEGER_MARKER]) + Or([number, _INTEGER_START, _INTEGER_END]))
            element = identifier + OneOrMore(row_element)
            parsed_elements = _parse_with_error_handling(element, line, self._start_index + index)

            row_idendtifier = parsed_elements[1][0]

            if row_idendtifier == _INTEGER_MARKER:
                self._handle_marker_line(parsed_elements[1][1])
                continue # skip this line

            columns.append(MPSColumns(
                identifier=parsed_elements[0],
                row_identifier=row_idendtifier,
                coeff=float(parsed_elements[1][1]),
                type=self._type
            ))

            # this means we have an additional column on the same line
            if len(parsed_elements) > 2:
                columns.append(MPSColumns(
                    identifier=parsed_elements[0],
                    row_identifier=parsed_elements[2][0],
                    coeff=float(parsed_elements[2][1]),
                    type=self._type
                ))

            if len(parsed_elements) > 3:
                raise MpsMalformedFileError(f"Found more than 2 rows identifier in a single '{SectionType.COLUMNS}' line")

        return columns


class RhsParser(SectionParser):
    """parses the RHS section of an .mps file into python objects"""

    def parse(self) -> List[MPSRhs]:
        # possible format 1 --> ['RHS1', ['R1', '2.0']]
        # possible format 2 --> ['RHS2', ['R2', '-2.0'], ['R3', '-1.0]]
        rhs = []
        for index, line in enumerate(self._lines):
            row_element = Group(identifier + number)
            element = identifier + OneOrMore(row_element)
            parsed_elements = _parse_with_error_handling(element, line, self._start_index + index)

            rhs.append(MPSRhs(
                identifier=parsed_elements[0],
                row_identifier=parsed_elements[1][0],
                coeff=float(parsed_elements[1][1])
            ))

            # this means we have an additional rhs on the same line
            if len(parsed_elements) > 2:
                rhs.append(MPSRhs(
                    identifier=parsed_elements[0],
                    row_identifier=parsed_elements[2][0],
                    coeff=float(parsed_elements[2][1])
                ))

            if len(parsed_elements) > 3:
                raise MpsMalformedFileError(f"Found more than 2 rows identifier in a single '{SectionType.RHS}' line")

        return rhs


class RangesParser(SectionParser):
    """parses the RANGES section of an .mps file into python objects"""

    def parse(self) -> List[MPSRanges]:
        # possible format 1 --> ['RNG1', ['R1', '2.0']]
        # possible format 2 --> ['RNG2', ['R2', '-2.0'], ['R3', '-1.0]]
        ranges = []
        for index, line in enumerate(self._lines):
            row_element = Group(identifier + number)
            element = identifier + OneOrMore(row_element)
            parsed_elements = _parse_with_error_handling(element, line, self._start_index + index)

            ranges.append(MPSRanges(
                identifier=parsed_elements[0],
                row_identifier=parsed_elements[1][0],
                coeff=float(parsed_elements[1][1]),
            ))

            # this means we have an additional range on the same line
            if len(parsed_elements) > 2:
                ranges.append(MPSRanges(
                    identifier=parsed_elements[0],
                    row_identifier=parsed_elements[2][0],
                    coeff=float(parsed_elements[2][1]),
                ))

            if len(parsed_elements) > 3:
                raise MpsMalformedFileError(f"Found more than 2 rows identifier in a single '{SectionType.RANGES}' line")

        return ranges


class BoundParser(SectionParser):
    """parses the BOUNDS section of an .mps file into python objects"""

    def parse(self) -> List[MPSBounds]:
        # possible format 1 --> ['UP', 'BND1', 'COL01', '1.0' ]
        # possible format 2 --> ['FR', 'BND2', 'COL02' ]
        bounds = []
        for index, line in enumerate(self._lines):
            element = bounds_type + identifier + identifier + Opt(number) + LineEnd()
            parsed_elements = _parse_with_error_handling(element, line, self._start_index + index)

            bounds.append(MPSBounds(
                identifier=parsed_elements[1],
                type=BoundsType(parsed_elements[0]),
                column_identifier=parsed_elements[2],
                value=float(parsed_elements[3]) if len(parsed_elements) > 3 else None
            ))

        return bounds


class QuadobjParser(SectionParser):
    """parses the QUADOBJ or QMATRIX section of an .mps file into python objects"""

    def __init__(self, start_index: int, lines: List[str], type: Union[SectionType.QUADOBJ, SectionType.QMATRIX]) -> None:
        super().__init__(start_index, lines)
        self._type = type

    def parse(self) -> List[MPSQuadobj]:
        # possible format --> ['x', 'x', 3]
        # possible format --> ['x', 'y', 1]
        quadobj = []
        for index, line in enumerate(self._lines):
            element = identifier + identifier + number + LineEnd()
            parsed_elements = _parse_with_error_handling(element, line, self._start_index + index)

            row = parsed_elements[0]
            column = parsed_elements[1]
            value = float(parsed_elements[2])

            quadobj.append(MPSQuadobj(row_identifier=row, column_identifier=column, value=float(parsed_elements[2])))

            # if QUADOBJ is set instead of QMATRIX, write another line but inversed to fulfill the matrix
            if self._type == SectionType.QUADOBJ and row != column:
                quadobj.append(MPSQuadobj(row_identifier=column, column_identifier=row, value=value))

        return quadobj


class EndataParser(SectionParser):
    """parses the ENDATA section of an .mps file into a python objects"""

    def parse(self) -> List[MPSEndata]:
        # possible format --> ['ENDATA'] # no need to parse here
        if len(self._lines) > 1:
            raise MpsMalformedFileError(f"Found more than 2 lines for section '{SectionType.ENDATA}'")

        return [MPSEndata()]