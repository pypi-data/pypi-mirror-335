# Copyright (c) 2024, InfinityQ Technology, Inc.
from typing import List
from warnings import warn

from .model import MPSObject
from .options import MPSParseOptions
from ._validations import (
    validate_missing_required_sections,
    validate_bounds_identifiers,
    validate_columns_identifiers,
    validate_ranges_identifiers,
    validate_rhs_identifiers
)
from ._visitor import LineSection
from ._section_parser import *
from ._section_reader import SectionReader


def parse_from_mps(path: str, options: MPSParseOptions) -> MPSObject:
    """
    import an .mps file and parse it as an MPSObject (python object)

    :param path: .mps file path
    :param options: MPSOptions if needed, default will be set if not provided

    :returns: A python like object of the .mps
    :rtype: MPSObject

    Example of this function:

    .. code-block:: python
    >>> mps_object = parse_from_mps("PATH_TO_FILE")
    >>> # name of the problem
    >>> name = mps_object.name
    >>> # first row sense
    >>> first_row = mps_object.rows[0].sense()
    """
    section_reader = SectionReader(path, options)
    parsed_lines_section: List[LineSection] = []

    # generator
    for section in section_reader.sections():
        parsed_lines_section.extend(section.parse())

    mps_object = MPSObject()
    for line in parsed_lines_section:
        line._accept(mps_object)

    _extract_objective_offset_if_any(mps_object)

    # post-validations
    validate_missing_required_sections(mps_object)
    validate_columns_identifiers(mps_object.rows, mps_object.free_row, mps_object.columns)
    validate_rhs_identifiers(mps_object.rows, mps_object.rhs)
    validate_ranges_identifiers(mps_object.rows, mps_object.ranges)
    validate_bounds_identifiers(mps_object.columns, mps_object.bounds)

    return mps_object


def export_to_mps(mps_object: MPSObject, path: str) -> None:
    raise NotImplementedError("Exporting to MPS is not currently supported")


def _extract_objective_offset_if_any(mps_object: MPSObject) -> None:
    """
    If the file contains an objective offset in the RHS section, simply extract it.

    If found, MPSObject will be modified in place and .objective_offset will be set.
    """
    original_list = mps_object.rhs

    free_row_identifier = mps_object.free_row.identifier()

    objective_offset_rows = [row for row in mps_object.rhs if row.row_identifier() == free_row_identifier]

    # remove all objective offset rows from the rhs list
    mps_object.rhs[:] = [row for row in mps_object.rhs if row.row_identifier() != free_row_identifier]
    assert mps_object.rhs is original_list, "original list was copied"

    for row in objective_offset_rows:
        if mps_object.objective_offset is None:
            mps_object.objective_offset = row
        else:
            warn(
                f"Found an objective offset '{row.coeff()}' identified as '{row.identifier()}', "
                f"but one was already identified with: '{mps_object.objective_offset.identifier()}'. Ignoring the new one."
            )