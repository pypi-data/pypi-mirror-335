# Copyright (c) 2024, InfinityQ Technology, Inc.
from typing import List, Optional

from titanq.errors import MpsMissingSectionError, MpsUnexpectedValueError
from .model import MPSBounds, MPSColumns, MPSObject, MPSRanges, MPSRhs, MPSRow
from .utils import SectionType


def _get_row_identifiers(rows: List[MPSRow], free_row: Optional[MPSRow] = False) -> List[str]:
    """returns a unique list of all ROWS identifiers, will include the free row if set to True"""
    identifiers = set([row.identifier() for row in rows])
    if free_row:
        identifiers.add(free_row.identifier())
    return identifiers


def _get_columns_identifiers(columns: List[MPSColumns]) -> List[str]:
    """returns a unique list of all COLUMNS identifiers, will include the free row if set to True"""
    return set([column.identifier() for column in columns])


def validate_columns_identifiers(rows: List[MPSRow], free_row: MPSRow, columns: List[MPSColumns]):
    """
    check if any row identifier in the columns does not match an existing row
    """
    rows_identifiers = _get_row_identifiers(rows, free_row)

    for column in columns:
        if column.row_identifier() not in rows_identifiers:
            raise MpsUnexpectedValueError(
                f"Found an unkown row identifier in the section '{SectionType.COLUMNS}': '{column.row_identifier()}'"
            )


def validate_rhs_identifiers(rows: List[MPSRow], rhs: List[MPSRhs]):
    """check if any rhs identifier in the columns does not match an existing row"""
    rows_identifiers = _get_row_identifiers(rows)
    for r in rhs:
        if r.row_identifier() not in rows_identifiers:
            raise MpsUnexpectedValueError(
                f"Found an unkown row identifier in the section '{SectionType.RHS}': '{r.row_identifier()}'"
            )


def validate_ranges_identifiers(rows: List[MPSRow], ranges: List[MPSRanges]):
    """check if any row identifier in the columns does not match an existing row"""
    rows_identifiers = _get_row_identifiers(rows)
    for range in ranges:
        if range.row_identifier() not in rows_identifiers:
            raise MpsUnexpectedValueError(
                f"Found an unkown row identifier in the section '{SectionType.RANGES}': '{range.row_identifier()}'"
            )


def validate_bounds_identifiers(columns: List[MPSColumns], bounds: List[MPSBounds]):
    """check if any column identifier is the bounds does not match an existing column"""
    columns_identifiers = _get_columns_identifiers(columns)

    for bound in bounds:
        if bound.column_identifier() not in columns_identifiers:
            raise MpsUnexpectedValueError(
                f"Found an unkown column identifier in the section '{SectionType.BOUNDS}': '{bound.column_identifier()}'"
            )

def validate_missing_required_sections(mps_object: MPSObject) -> None:
    """check if any of the required section is missing"""
    missing_section = None
    if mps_object.name == None:
        missing_section = SectionType.NAME
    elif len(mps_object.rows) == 0 :
        missing_section = SectionType.ROWS
    elif len(mps_object.columns) == 0:
        missing_section = SectionType.COLUMNS
    elif len(mps_object.rhs) == 0:
        missing_section = SectionType.RHS
    elif not mps_object.endata:
        missing_section = SectionType.ENDATA

    if missing_section:
        raise MpsMissingSectionError(f"Section '{missing_section}' was not found, this section is required in an .mps file")