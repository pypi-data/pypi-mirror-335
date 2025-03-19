# Copyright (c) 2024, InfinityQ Technology, Inc.
"""
This module provides utilities for symbolic mathematics and optimization, leveraging the SymEngine library. It streamlines the representation,
manipulation, and transformation of symbolic expressions and equations into formats suitable for titanQ.

Responsibilities:
------------------
- Encapsulating SymEngine objects in a user-friendly interface to enhance usability.
- Enabling representation and manipulation of symbolic expressions via the `Expression` class.
- Facilitating the creation and conversion of symbolic equations (`Equation` class) into constraints for optimization.
- Expanding symbolic terms into their constituent variables and coefficients.
- Generating matrices for TitanQ (e.g., bias, weight, constraint mask) from expressions and equations.

Why Use This Module:
---------------------
- Provides a fast and intuitive way to define and manipulate expressions and equations.
- Incorporates warnings and safeguards to assist users in debugging their symbolic formulations.

Potential Enhancements:
------------------------
- **Support for Additional Equation Types**: Extend capabilities to include quadratic or higher-degree constraints.
- **Enhanced Warnings and Safeguards**: Introduce more detailed messages for unsupported features and edge cases.

Limitations:
------------
1. **Avoid Generic Numerical Solvers**: This module is dedicated to symbolic manipulation and preparing optimization tasks, not for solving numerical equations directly.
2. **Exclude Non-Symbolic Utilities**: Maintain a clear focus on symbolic mathematics and optimization-related functionalities.

Example Usage:
---------------
```python
# Create a model
from titanq import Model
model = Model()

# Create variable vectors
x = model.add_variable_vector('x', 10)
y = model.add_variable_vector('y', 10)

# Define an objective function using an expression
model.set_objective_expression(sum(x + y) + y**2)

# Add a constraint from an expression
model.add_constraint_from_expression(x[2] > y[4])
```
"""


from collections import defaultdict
from typing import Any, Dict, NamedTuple, Tuple, Union
import warnings

import numpy as np
from numpy.typing import NDArray
import symengine as se
import symengine.lib.symengine_wrapper as se_type

from .variables import Variable
from ..errors import ContradictoryExpressionError, TautologicalExpressionError


class ExpressionComponent(NamedTuple):
    constant: float
    linear: NDArray
    quadratic: NDArray


class ExpandedVariableList:
    """
    A class representing an expanded list of variables that can be safely used as dictionary keys.

    The `ExpandedVariableList` ensures that instances are hashable and can be compared reliably.
    This makes it suitable for use in scenarios where a list-like structure must serve as a key in a dictionary.

    Features:
    - Ensures immutability to guarantee consistent hash values.
    - Implements custom equality and hashing to allow comparison based on the content of the list.
    """
    def __init__(self, *variables: Variable) -> None:
        # Save _variables as tuple so it can be easily hashed and compared later.
        self._variables = tuple(sorted(variables, key=lambda v: v.problem_index()))


    def __hash__(self):
        return hash(self._variables)


    def __eq__(self, other):
        if isinstance(other, ExpandedVariableList):
            return self._variables == other._variables
        return False


    def __repr__(self):
        return repr(self._variables)


    def __iter__(self):
        return iter(self._variables)


    def __len__(self):
        return len(self._variables)


    def __getitem__(self, index):
        return self._variables[index]



class SymEngineObjectWrapper():
    """
    A wrapper class for encapsulating SymEngine objects, providing a convenient interface for representation
    and ensuring type safety.

    This class serves as a common parent for all mathematical objects, primarily to support the _get_se_object function.
    """

    def __init__(self, se_object: se_type.Basic):
        if not isinstance(se_object, se_type.Basic):
            raise TypeError(f"Expected an object of type symengine.Basic, got {type(se_object)}.")

        self._se_object = se_object


    def __repr__(self) -> str:
        return repr(self._se_object)


    def __str__(self) -> str:
        return str(self._se_object)

class Expression(SymEngineObjectWrapper):
    """
    A class for representing and manipulating mathematical expressions based on SymEngine.
    """

    def expand(self) -> 'Expression':
        """
        Expand the current expression algebraically.

        Returns
        -------
            Expression: A new expanded expression.
        """
        return Expression(se.expand(self._se_object))


    def terms(self) -> Dict[ExpandedVariableList, float]:
        """
        Decompose the expression into individual terms and their coefficients.

        Returns
        -------
            A mapping of variable tuples to their coefficients.
        """
        d = defaultdict(lambda: 0)
        for term, coeff in self._se_object.as_coefficients_dict().items():
            vars = _expand_term(term)
            d[vars] += coeff
        return d


    def split_into_component(self, n_variable: int) -> ExpressionComponent:
        """
        Convert the expression into constant, bias, and weight matrices.

        Returns
        -------
            - Constant term,
            - Bias vector,
            - Weight matrix (or None if no quadratic terms are present).

        Raise
        ------
            - ValueError: If n_variable is n <= 0.
            - ValueError: If The equation degree exceeds 2.
        """
        if n_variable <= 0:
            raise ValueError("Cannot generate matrices from expression for a non-positive number of variables")

        expr = self.expand()

        const = 0
        bias = np.zeros(n_variable, dtype=np.float32)
        weights = np.zeros((n_variable, n_variable), dtype=np.float32)

        for vars, coeffs in expr.terms().items():
            n_vars = len(vars)

            if n_vars == 0:
                const += coeffs
            elif n_vars == 1:
                bias[vars[0].problem_index()] += coeffs
            elif n_vars == 2:
                index1, index2 = vars[0].problem_index(), vars[1].problem_index()
                weights[index1, index2] += coeffs
                weights[index2, index1] += coeffs
            else:
                raise ValueError("Currently only equations of degree 2 or lower are supported.")

        if np.all(weights == 0):
            return const, bias, None
        return const, bias, weights


    def __neg__(self) -> 'Expression':
        return Expression(-self._se_object)


    def __add__(self, other) -> 'Expression':
        return Expression(self._se_object + _get_se_object(other))


    def __sub__(self, other) -> 'Expression':
        return Expression(self._se_object - _get_se_object(other))


    def __mul__(self, other) -> 'Expression':
        return Expression(self._se_object * _get_se_object(other))


    def __pow__(self, other) -> 'Expression':
        return Expression(self._se_object ** other)


    def __radd__(self, other) -> 'Expression':
        return Expression(_get_se_object(other) + self._se_object)


    def __rsub__(self, other) -> 'Expression':
        return Expression(_get_se_object(other) - self._se_object)


    def __rmul__(self, other) -> 'Expression':
        return Expression(_get_se_object(other) * self._se_object)


    def __eq__(self, other) -> 'Equation':
        return Equation(se.Equality(self._se_object, _get_se_object(other)))


    def __ne__(self, other) -> 'Equation':
        return Equation(se.Unequality(self._se_object, _get_se_object(other)))


    def __le__(self, other) -> 'Equation':
        return Equation(self._se_object <= _get_se_object(other))


    def __lt__(self, other) -> 'Equation':
        return Equation(self._se_object < _get_se_object(other))


    def __ge__(self, other) -> 'Equation':
        return Equation(self._se_object >= _get_se_object(other))


    def __gt__(self, other) -> 'Equation':
        return Equation(self._se_object > _get_se_object(other))


class Equation(SymEngineObjectWrapper):
    """
    Represents a symbolic equation that can be converted into constraints for optimization.
    """

    def __init__(self, se_object):
        if isinstance(se_object, se_type.BooleanTrue): # Tautological Expression alway resolve to true
            raise TautologicalExpressionError()
        if isinstance(se_object, se_type.BooleanFalse):# Contradictory Expression alway resolve to false
            raise ContradictoryExpressionError()
        super().__init__(se_object)

    def generate_constraint(self, n_variable: int) -> Tuple[NDArray, NDArray]:
        """
        Generate a constraint mask and bounds from the symbolic equation.

        Returns
        -------
            - Constraint Mask
            - Constraint Bound

        Raise
        ------
            - ValueError: If n_variable is n <= 0.
            - ValueError: If the equation contains non-linear (quadratic or higher) terms.

        Warnings
        --------
            - Strict inequalities (e.g., <, >) are treated as non-strict (<=, >=).
        """
        if n_variable <= 0:
            raise ValueError("Cannot generate constraints object from equation for a non-positive number of variables")


        lhs, rhs = Expression(self._se_object.args[0]), Expression(self._se_object.args[1])
        eq = (rhs-lhs).expand()

        mask = np.zeros(n_variable, dtype=np.float32)
        const = 0

        for vars, coeffs in eq.terms().items():
            n_vars = len(vars)

            if n_vars == 0:
                const += coeffs
            elif n_vars == 1:
                mask[vars[0].problem_index()] += coeffs
            else:
                raise ValueError(
                    "Quadratic terms are not supported in constraints. "
                    "Please ensure that the expression contains only linear terms when using it as a constraint."
                )

        const = -const # inverse constant because it should be on the other side of the equation

        bounds = []
        if isinstance(self._se_object, se_type.Equality):
            bounds = [const, const]
        elif isinstance(self._se_object, se_type.LessThan):
            bounds = [const, np.nan]
        else: # strictly lesser than

            warnings.warn(
                "TitanQ does not support strictly less than (<) or strictly greater than (>) constraints."
                "These will be treated as less than or equal to (<=) or greater than or equal to (>=) constraints instead."
                "If this behavior is not desired, please revise the expression accordingly."
            )
            bounds = [const, np.nan]

        return mask, np.array(bounds, dtype=np.float32)


def _get_se_object(self: Union['SymEngineObjectWrapper', Any]) -> Union[se_type.Basic, Any]:
    """
    Return the underlying symengine object if the object is a SymengineObjectWrapper.
    Otherwise, return the object itself.

    Returns
    -------
        The unwrapped symengine object or the original object.
    """
    if isinstance(self, SymEngineObjectWrapper):
        return self._se_object
    else:
        return self


def _expand_term(term: se_type.Basic) -> ExpandedVariableList:
    """
    Decompose a mathematical term into its constituent variables.

    Returns
    -------
        A tuple containing the expanded variables.

    Raise
    ------
        NotImplementedError: If the term type is not supported.

    Example
    -------
        >>> expand_term(x * y)
        (x, y)
        >>> expand_term(x**3 * y**2)
        (x, x, x, y, y)
    """
    # Constant term
    if isinstance(term, (se_type.One, se_type.Zero)):
        return ExpandedVariableList()

    # Case for a single variable
    if isinstance(term, se_type.Symbol):
        return ExpandedVariableList(term)

    # Multiple variables of the same
    if isinstance(term, se_type.Pow):
        return ExpandedVariableList(*[term.base] * int(term.exp))

    # Multiple different variable
    if isinstance(term, se_type.Mul):
        return ExpandedVariableList(*(var for arg in term.args for var in _expand_term(arg)))

    raise NotImplementedError(f"Cannot split term into individual variable (type={type(term)})")