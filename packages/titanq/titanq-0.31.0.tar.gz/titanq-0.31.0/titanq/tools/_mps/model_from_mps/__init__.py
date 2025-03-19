# Copyright (c) 2024, InfinityQ Technology, Inc.

"""
This module offers methods to define a :class:`Model` from a MPS file.
"""

from collections import defaultdict
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from deprecated.sphinx import deprecated
import numpy as np

from titanq import Model, Vtype

from .bounds import ConstraintBounds, VariableBounds
from titanq.errors import MpsConfiguredModelError, MpsUnexpectedValueError, MpsUnsupportedError
from ..mps_parser import (
    BoundsType,
    ColumnsType,
    MPSBounds,
    MPSColumns,
    MPSObject,
    MPSQuadobj,
    MPSParseOptions,
    MPSRhs,
    parse_from_mps,
    RowsType
)
from .utils import SetOnceOrDefault, get_variables_and_types


def from_mps(
    path: Union[str, os.PathLike],
    model: Model,
    *,
    skip_empty_lines: bool = False,
) -> None:
    """
    Configure a model from an .mps file. It currently supports these following sections.

    - NAME: The name of the problem.
    - ROWS: The definition of constraints.
    - COLUMNS: The coefficients for the variables.
    - RHS: The right-hand side values for the constraints.
    - BOUNDS: The bounds on the variables.
    - QUADOBJ or QMATRIX: The quadratic objective matrix
    - ENDATA: Marks the end of the data.

    Integer variables in .mps files are supported both by the markers in the COLUMNS section 
    and from the types in the BOUNDS section.

    Parameters
    ----------
    path
        The path to the .mps file
    model
        The instance of the model to configure. Must not be already
        configured.
    options
        Additional options applied when parsing the .mps file

    Raises
    ------
    OSError, FileNotFoundError
        If the specified MPS file path cannot be open.
    :class:`titanq.errors.MpsConfiguredModelError`
        If the provided model already contains data (e.g. variables).
    :class:`titanq.errors.MpsParsingError`
        If the provided MPS file cannot be parsed.

    Example
    -------
    >>> from titanq.tools import from_mps
    >>> from titanq import Model
    >>> model = Model()
    >>> from_mps("path/to/file.mps", model)
    >>> model.optimize()
    """
    # validate the model is empty
    if len(model._variables) > 0:
        raise MpsConfiguredModelError(
            "Found variables in the model for the .mps file parser."
            "Did you pass a pre-configured model? The model must be empty."
        )

    mps_object = parse_from_mps(path, MPSParseOptions(skip_empty_lines=skip_empty_lines))

    # build a unique list of variables from the COLUMNS with their corresponding types
    # example [('COL01', ColumnsType.CONTINUOUS), ('COL02', ColumnsType.CONTINUOUS)]
    variables = get_variables_and_types(mps_object.columns)

    # build a dictionary mapping each variable name to their indices which allows
    # an average of O(1) instead of O(n) when trying to find the index of a variable identifier
    # example { 'COL1': 0, 'COL2': 1 }
    variables_map = { item[0]: index for index, item in enumerate(variables) }

    # create variables with their name, type and bounds
    _create_variables(model, variables, mps_object.bounds)

    # weights and bias
    weights = _get_weights(variables_map, mps_object.quadobj)
    bias = _get_bias(variables, mps_object.columns, mps_object.free_row.identifier())
    model.set_objective_matrices(weights, bias)

    # constraints
    _create_constraints(model, variables_map, mps_object)


@deprecated(version="0.26.0", reason="Use :func:`from_mps` instead.")
def configure_model_from_mps_file(model: Model, file_path: Path) -> None:
    """
    Deprecated. Alternative form of :func:`from_mps`.

    Parameters
    ----------
    model
        The instance of the model to configure.
    file_path
        The path to the MPS file.
    """
    from_mps(file_path, model)


def _get_weights(variables_map: Dict, quadobj: List[MPSQuadobj]) -> Optional[np.ndarray]:
    if len(quadobj) == 0:
        return None

    variables_length = len(variables_map)
    weights = np.zeros((variables_length, variables_length), dtype=np.float32)

    for row in quadobj:
        weights[variables_map[row.row_identifier()]][variables_map[row.column_identifier()]] = row.value()

    return weights


def _get_bias(variables: List[str], columns: List[MPSColumns], objective_identifier: str) -> np.ndarray:
    """obtain bias values from the COLUMNS section, the objective identifier is the bias"""
    variables_dict = defaultdict(lambda:
        SetOnceOrDefault(0, "Variable with more than one objective value", allow_same_value=True)
    )

    # read bias values from the columns
    for column in columns:
        if column.row_identifier() == objective_identifier:
            variables_dict[column.identifier()].set(column.coeff())

    bias = []
    for name, _ in variables:
        bias.append(variables_dict[name].get())

    return np.array(bias, dtype=np.float32)


def _create_variables(model: Model, variables: List[Tuple[str, ColumnsType]], bounds: List[MPSBounds]) -> None:
    """obtain the variables bounds from the BOUNDS section"""
    var_bounds_dict = defaultdict(lambda: VariableBounds(0.0, np.nan, Vtype.CONTINUOUS))
    for bound in bounds:
        type = bound.type()
        value = bound.value()
        var_bound = var_bounds_dict[bound.column_identifier()]

        # in the following statements, we want to override vtype for each entry
        # to avoid types mixins. Bounds object will not tolerate it
        if type == BoundsType.LOWER_BOUND:
            var_bound.set(lower=value, vtype=Vtype.CONTINUOUS)
        elif type == BoundsType.LOWER_BOUND_INT:
            var_bound.set(lower=value, vtype=Vtype.INTEGER)
        elif type == BoundsType.UPPER_BOUND:
            var_bound.set(upper=value, vtype=Vtype.CONTINUOUS)
        elif type == BoundsType.UPPER_BOUND_INT:
            var_bound.set(upper=value, vtype=Vtype.INTEGER)
        elif type == BoundsType.FIXED_VALUE: # upper and lower bound the same
            var_bound.set(lower=value, upper=value, vtype=Vtype.CONTINUOUS)
        elif type == BoundsType.FREE_VARIABLE: # lower bound -∞ and upper bound +∞
            var_bound.set(lower=-np.nan, upper=np.nan, vtype=Vtype.CONTINUOUS)
        elif type == BoundsType.MINUS_INFINITY: # lower bound = -∞
            var_bound.set(lower=-np.nan, vtype=Vtype.CONTINUOUS)
        elif type == BoundsType.PLUS_INFINITY: # upper bound = +∞
            var_bound.set(upper=np.nan, vtype=Vtype.CONTINUOUS)
        elif type == BoundsType.BINARY_VARIABLE:
            var_bound.set(vtype=Vtype.BINARY)
        elif type == BoundsType.SEMI_CONTINUOUS:
            raise MpsUnsupportedError(f"Type of bound '{BoundsType.SEMI_CONTINUOUS}' is not supported by TitanQ")
        else:
            # this should never happen, as it is handled by the parser
            raise Exception(f"Unknown type of bound '{type}'")

    # set variables
    for name, type in variables:
        variable_bound = var_bounds_dict[name]

        # unless the bounds are defined as BINARY, we override the variable type and the bounds if not set because
        # the variable type is defined in the columns section with a marker, this is the result of the integer extensions.
        variable_is_integer = not variable_bound.is_binary() and type == ColumnsType.INTEGER

        variable_bound.into_model_variable(model, name, variable_is_integer)


def _get_constraint_weights(
    variables_map: Dict[str, int],
    columns: List[MPSColumns],
    objective_identifier: str,
    constraints_name: List[str],
) -> None:
    """obtain the constraints weights from the COLUMN section"""
    variables_length = len(variables_map)
    num_constraints = len(constraints_name)

    constraint_weights = np.zeros((num_constraints, variables_length), dtype=np.float32)
    for column in columns:
        # ignore objective column
        if column.row_identifier() == objective_identifier:
            continue

        column_index = variables_map[column.identifier()]
        row_index = constraints_name.index(column.row_identifier())
        constraint_weights[row_index][column_index] = column.coeff()

    return constraint_weights


def _get_constraint_bounds(rhs: List[MPSRhs], constraints_dict: dict, constraints_name: List[str]):
    """obtain the constraints bounds from the RHS and RANGES section"""
    constraints_bounds_dict = defaultdict(lambda: ConstraintBounds(0.0, 0.0))
    for r in rhs:
        constraint = constraints_dict[r.row_identifier()]
        sense = constraint["sense"]
        range = constraint["range"] if constraint["range"] else np.nan
        constraint_bound = constraints_bounds_dict[r.row_identifier()]

        if sense == RowsType.GREATER_OR_EQUAL: # [Lower: rhs, Upper: rhs + |range|]
            constraint_bound.set(lower=r.coeff(), upper=r.coeff() + abs(range))
        elif sense == RowsType.LOWER_OR_EQUAL: # [Lower: rhs - |range|, Upper: rhs]
            constraint_bound.set(lower=r.coeff() - abs(range), upper=r.coeff())
        elif sense == RowsType.EQUALITY:
            constraint_bound.set(lower=r.coeff(), upper=r.coeff())
        elif sense == RowsType.FREE_ROW:
            # this should never happen, as it is handled by the parser
            raise MpsUnexpectedValueError("Found a free row while trying to create constraint bounds")
        else:
            # this should never happen, as it is handled by the parser
            raise Exception(f"Unknown type of sense '{sense}'")

    constraint_bounds = []
    for constraint_name in constraints_name:
        lower, upper = constraints_bounds_dict[constraint_name].get()
        constraint_bounds.append([lower, upper])

    return constraint_bounds


def _create_constraints(model: Model, variables_map: Dict[str, int], mps: MPSObject) -> None:
    """Append the constraint weights and the constrain bounds to the model from the MPS object."""
    # pre process to iterate less. Find each of the constraints sense and range.
    # this will enable iterating over ROWS and RANGE only once
    constraints_dict = {}
    for row in mps.rows:
        constraints_dict[row.identifier()] = { "sense": row.sense(), "range": None }
    for range in mps.ranges:
        constraints_dict[range.row_identifier()]["range"] = range.coeff()

    # keys as a list
    constraints_name = list(constraints_dict.keys())

    # constraint weights
    constraint_weights = _get_constraint_weights(variables_map, mps.columns, mps.free_row.identifier(), constraints_name)

    # constraint bounds
    constraint_bounds = _get_constraint_bounds(mps.rhs, constraints_dict, constraints_name)

    # add constraints to the model
    for index, constraint in enumerate(constraints_dict):
        sense = constraints_dict[constraint]["sense"]
        if sense == RowsType.GREATER_OR_EQUAL or sense == RowsType.LOWER_OR_EQUAL:
            model.add_inequality_constraint(
                constraint_mask=np.array(constraint_weights[index], dtype=np.float32),
                constraint_bounds=np.array(constraint_bounds[index], dtype=np.float32)
            )
        elif sense == RowsType.EQUALITY:
            model.add_equality_constraint(
                constraint_mask=np.array(constraint_weights[index], dtype=np.float32),
                limit=np.array(constraint_bounds[index][0], dtype=np.float32) # does not matter here upper or lower
            )
