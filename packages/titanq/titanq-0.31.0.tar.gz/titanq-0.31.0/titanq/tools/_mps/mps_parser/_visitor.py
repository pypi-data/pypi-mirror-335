# Copyright (c) 2024, InfinityQ Technology, Inc.
import abc


class Visitor(abc.ABC):
    """Visitor class containing all visit methods"""
    def _visit_name(self, name):
        pass

    def _visit_rows(self, row):
        pass

    def _visit_free_row(self, row):
        pass

    def _visit_columns(self, column):
        pass

    def _visit_rhs(self, rhs):
        pass

    def _visit_ranges(self, range):
        pass

    def _visit_bounds(self, bound):
        pass

    def _visit_quadobj(self, quadobj):
        pass

    def _visit_endata(self):
        pass

class LineSection(abc.ABC):
    """This is the base class for a line of a section of the MPS file"""

    def _accept(self, visitor: Visitor):
        pass