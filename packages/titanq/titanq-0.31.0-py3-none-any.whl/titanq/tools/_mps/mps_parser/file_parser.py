# Copyright (c) 2024, InfinityQ Technology, Inc.
from typing import List

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

    # post-validations
    validate_missing_required_sections(mps_object)
    validate_columns_identifiers(mps_object.rows, mps_object.free_row, mps_object.columns)
    validate_rhs_identifiers(mps_object.rows, mps_object.rhs)
    validate_ranges_identifiers(mps_object.rows, mps_object.ranges)
    validate_bounds_identifiers(mps_object.columns, mps_object.bounds)

    return mps_object


def export_to_mps(mps_object: MPSObject, path: str) -> None:
    raise NotImplementedError("Exporting to MPS is not currently supported")