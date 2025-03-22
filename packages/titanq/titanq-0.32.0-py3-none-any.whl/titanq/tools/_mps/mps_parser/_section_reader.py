# Copyright (c) 2024, InfinityQ Technology, Inc.
from typing import Any, Generator, Optional

from .options import MPSParseOptions
from ._section_parser import (
    BoundParser,
    ColumnParser,
    EndataParser,
    NameParser,
    QuadobjParser,
    RangesParser,
    RhsParser,
    RowsParser,
    SectionParser
)
from .utils import SectionType


class SectionReader:
    """
    Reads an MPS file and generate section by section with
    the method sections()
    """
    def __init__(self, path: str, options: MPSParseOptions) -> None:
        self._path = path
        self._options = options


    def _new_section(self, line: str) -> Optional[SectionType]:
        """returns a section if encountered a new one, returns None otherwise"""
        # an exception for NAME, where the value is on the same line
        if line.startswith(SectionType.NAME):
            return SectionType.NAME

        for section in [section.value for section in SectionType]:
            if line == section:
                return section
        return None


    def sections(self) -> Generator[SectionParser, Any, Any]:
        """generate sections by yielding one at a time"""
        current_section = None
        lines = []

        # open context manager is already lazy loading, since
        # the file is line-based. This way it loads into memory by chunks
        section_start_index = 1
        with open(self._path, 'r') as file:
            for line_index, line in enumerate(file, start=1):
                line = line.strip() # always strip the line
                if self._options.empty_line_check(line_index, line):
                    continue

                new_section = self._new_section(line)
                # this means we have entered a new section, we need to yield the old one
                if new_section is not None:
                    if current_section == SectionType.ROWS:
                        yield RowsParser(section_start_index, lines)
                    elif current_section == SectionType.COLUMNS:
                        yield ColumnParser(section_start_index, lines)
                    elif current_section == SectionType.RHS:
                        yield RhsParser(section_start_index, lines)
                    elif current_section == SectionType.RANGES:
                        yield RangesParser(section_start_index, lines)
                    elif current_section == SectionType.BOUNDS:
                        yield BoundParser(section_start_index, lines)
                    elif current_section == SectionType.QUADOBJ:
                        yield QuadobjParser(section_start_index, lines, SectionType.QUADOBJ)
                    # same as QUADOBJ, but QMATRIX specifies each entry of the matrix
                    elif current_section == SectionType.QMATRIX:
                        yield QuadobjParser(section_start_index, lines, SectionType.QMATRIX)

                    # NAME and ENDATA yield immediatly
                    if new_section == SectionType.NAME:
                        yield NameParser(section_start_index, [line])
                    elif new_section == SectionType.ENDATA:
                        yield EndataParser(section_start_index, [line])
                        break # end of file, stop here

                    lines = []
                    current_section = new_section
                    section_start_index = line_index + 1
                else:
                    lines.append(line) # just add the line
