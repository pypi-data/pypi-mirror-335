# Copyright (c) 2024, InfinityQ Technology, Inc.
import io
import json
import logging
from pickle import UnpicklingError
import numpy as np
import numpy.typing as npt
import zipfile

from pydantic import ValidationError
from typing import Any, Dict, List, Optional, Tuple, Union

from titanq._model.array import Array
from titanq._model.array.factory import ArrayLikeFactory
from .constraints import (
    Constraints,
    get_constraint_type,
    QuadConstraints,
)
from ..errors import (
    ConstraintAlreadySetError,
    MissingVariableError,
    ObjectiveAlreadySetError,
)

from .manifest import Manifest
from .numpy_util import (
    is_ndarray_binary,
    is_upperbound_bigger_equal_lowerbound,
    ndarray_contains_nan_inf,
    reshape_to_2d,
    validate_cardinalities
)
from .objective import Objective, Target
from .optimize_response import OptimizeResponse
from .precision import Precision
from .math_object import Equation, Expression
from .variables import BinaryVariable, ContinuousVariable, IntegerVariable, Variable, Vtype

from .._client import api_model, Client
from .._storage import ManagedStorage, StorageClient, Ftype, to_bytes
from titanq import errors

log = logging.getLogger("TitanQ")


class Model:
    """
    Root object to define a problem to be optimized
    """

    def __init__(
        self,
        *,
        api_key: str = None,
        storage_client: StorageClient = None,
        base_server_url: str = "https://titanq.infinityq.io"
        ) -> None:
        """
        Initiate the model with a storage client. If the storage_client is missing, the storage will be managed by TitanQ.

        Notes
        -----
        If the storage is managed by TitanQ, the total input files size is limited to 1GB.

        Parameters
        ----------
        api_key
            TitanQ API key to access the service.
            If not set, it will use the environment variable ``TITANQ_API_KEY``
        storage_client
            Storage to choose in order to store some items.
        base_server_url
            TitanQ API server url, default set to ``https://titanq.infinityq.io``.

        Raises
        ------
        MissingTitanqApiKey
            If no API key is set and is also not set as an environment variable

        Examples
        --------
        With an S3 storage client
            >>> from titanq import Model, S3Storage
            >>> storage_client = S3Storage(
                access_key="{insert aws bucket access key here}",
                secret_key="{insert aws bucket secret key here}",
                bucket_name="{insert bucket name here}"
            )
            >>> model = Model(storage_client)

        Managed storage client
            >>> from titanq import Model, S3Storage
            >>> model = Model()
        """
        self._variables: List[Variable] = []
        self._objective: Objective = None
        self._constraints = Constraints()
        self._quad_constraints = QuadConstraints()

        self._titanq_client = Client(api_key, base_server_url)
        self._manifest: Manifest = Manifest()

        # the user chose a managed storage or left it as default
        if storage_client is None:
            storage_client = ManagedStorage(self._titanq_client)

        self._storage_client: StorageClient = storage_client


    def get_objective_matrices(self) -> Tuple[Optional[Array], Optional[np.ndarray]]:
        """
        Retrieve the weights and bias vector from the model's objective. Both will be None
        if not set.

        Return
        ------
        Weights matrix and the bias vector if the objective has been set, else both will be None
        """
        if self._objective is not None:
            weights = self._objective.weights().array() if self._objective.weights() else None
            bias = self._objective.bias().array()
            return weights, bias

        return (None, None)


    def get_constraints_weights_and_bounds(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Retrieve the weights and bounds of all constraints from the model.

        Return
        ------
        Constraints weights if not None and constraints bounds if not None
        """
        return self._constraints.weights(), self._constraints.bounds()


    def get_quad_constraints_weights_and_bounds(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Retrieve the quadratic constraints weights and bounds.

        Return
        ------
        Quadratic constraints weights if not None and quadratic constraints bounds if not None
        """
        return self._quad_constraints.weights(), self._constraints.bounds()


    def get_quad_constraints_linear_weights(self) -> Optional[np.ndarray]:
        """
        Retrieve the quadratic constraints linear weights.

        Return
        ------
        Quadratic constraints linear weights if not None
        """
        return self._quad_constraints.linear_weights()


    def add_variable_vector(
        self,
        name: str = '',
        size: int = 1,
        vtype: Vtype = Vtype.BINARY,
        variable_bounds:
            Optional[
                Union[
                    List[Tuple[int, int]],
                    List[Tuple[float, float]],
                ]
            ]=None,
    ) -> npt.NDArray[Any]:
        """
        Add a vector of variable to the model. Multiple variables vector can be added but with different names.

        Notes
        -----
        If Vtype is set to ``Vtype.INTEGER`` or ``Vtype.CONTINUOUS``, variable_bounds need to be set.

        Parameters
        ----------
        name
            The name given to this variable vector.
        size
            The size of the vector.
        vtype
            Type of the variables inside the vector.
        variable_bounds
            Lower and upper bounds for the variable vector. A list of tuples (can be either integers or continuous)

        Return
        ------
        variable
            The variable vector created.

        Raises
        ------
        MaximumVariableLimitError
            If the total size of variables exceed the limit.
        ValueError
            If the size of the vector is < 1

        Examples
        --------
        >>> from titanq import Model, Vtype
        >>> model.add_variable_vector('x', 3, Vtype.BINARY)
        >>> model.add_variable_vector('y', 2, Vtype.INTEGER, [[0, 5], [1, 6]])
        >>> model.add_variable_vector('z', 3, Vtype.CONTINUOUS, [[2.3, 4.6], [3.1, 5.3], [1.1, 4]])
        """

        if not variable_bounds:
            variable_bounds = []

        # validation
        if not self._constraints.is_empty() or not self._quad_constraints.is_empty():
            raise ConstraintAlreadySetError(
                "Cannot add additional variables once linear or quadratic " \
                "constraints have been defined")

        if self._objective is not None:
            raise ObjectiveAlreadySetError("Cannot add additional variable once objective have been defined")

        if vtype is Vtype.BINARY and variable_bounds:
            raise ValueError("variable_bounds is not supported with Vtype.BINARY")

        if size < 1:
            raise ValueError("Variable vector size cannot be less than 1")

        # create the variable
        variables = []
        if vtype is Vtype.BINARY:
            variables = [BinaryVariable(name, i, len(self._variables) + i) for i in range(size) ]
        elif vtype is Vtype.INTEGER:
            variables = [IntegerVariable(name, i, len(self._variables) + i, variable_bounds[i]) for i in range(size)]
        elif vtype is Vtype.CONTINUOUS:
            variables = [ContinuousVariable(name, i, len(self._variables)+i, variable_bounds[i]) for i in range(size)]
        else:
            raise NotImplementedError(f"Unsupported variable type: {vtype}")

        self._variables.extend(variables)
        log.debug(f"add variable name='{name}', type={str(vtype)}, size={size}.")

        return np.array([Expression(v) for v in variables])


    def set_objective_expression(self, expr: Expression, target=Target.MINIMIZE):
        """
        ℹ️ **This feature is experimental and may change.**

        Sets the objective function for the optimization problem using the given expression.

        This method processes the provided expression to extract the bias vector and weight matrix,
        and then sets these as the objective matrices for the optimization problem.

        Parameters
        ----------
        expr
            The expression defining the objective function.
        target
            The target of this objective matrix.

        Raises
        ------
        TypeError
            if the provided expression contains any invalid/unsupported input

        Examples
        --------
        >>> from titanq import Model, Vtype
        >>> x = model.add_variable_vector('x', 2, Vtype.BINARY)
        >>> y = model.add_variable_vector('y', 2, Vtype.BINARY)
        >>> expr = (np.array([3, 4]) * x + (x * y) - 5 * y)[0]
        >>> model.set_objective_expression(expr)
        """
        if not isinstance(expr, Expression):
            raise TypeError(f"The given objective expression is not of type {str(Expression)}.")

        constant, bias, weights = expr.split_into_component(len(self._variables))
        self.set_objective_matrices(weights, bias, target, constant)


    def add_constraint_from_expression(self, equation: Equation):
        """
        ℹ️ **This feature is experimental and may change.**

        Adds a constraint to the model using the given expression.

        This method processes the provided constraint expression to add it as a constraint to the
        optimization problem. Only linear constraints of the following types are supported:

        - `A == B`
        - `A <  B`
        - `A <= B`
        - `A >  B`
        - `A >= B`

        Constraints involving quadratic terms cannot be added as
        expressions and will raise an error.
        Instead, use :meth:`add_quadratic_equality_constraint` or
        :meth:`add_quadratic_inequality_constraint`.

        Parameters
        ----------
        expression
            The constraint expression. This should be an instance of `Equation`.

        Raises
        ------
        ValueError
            If the provided expression contains quadratic terms.
        TypeError
            If the provided expression is of an invalid or unsupported type.

        Examples
        --------
        >>> from titanq import Model, Vtype
        >>> x = model.add_variable_vector('x', 2, Vtype.BINARY)
        >>> y = model.add_variable_vector('y', 2, Vtype.BINARY)
        >>> expr = sum(x+y) == 1
        >>> model.add_constraint_from_expression(expr)
        """
        if not isinstance(equation, Equation):
            raise TypeError(f"The given constraint equation is not of type {str(Equation)}.")

        n_variable = len(self._variables)
        mask, bounds = equation.generate_constraint(n_variable)

        self._constraints.add_constraint(
            num_variables=n_variable,
            constraint_weights=reshape_to_2d(mask),
            constraint_bounds=reshape_to_2d(bounds)
        )


    def set_objective_matrices(
        self,
        weights: Optional[Array],
        bias: np.ndarray,
        target=Target.MINIMIZE,
        constant_term: float=0.0
    ) -> None:
        """
        Set the objective matrices for the model.

        Parameters
        ----------
        weights
            The quadratic objective matrix, **this matrix needs to be symmetrical**.
            A NumPy 2-D dense ndarray (must be float32) or A SciPy 2-D sparse coo_array (must be float32).
            Weights matrix can be set to **None** if it is a linear problem with no quadratic elements.
        bias
            The linear constraint vector. A NumPy 1-D ndarray.
        target
            The target of this objective matrix.
        constant_term
            This parameter represents a fixed value added to the final computed objective value.

            Example: Suppose the objective function to minimize is 'f(x) = x^2 + 2x + 4' and 'x' is a binary variable.

            The optimal solution would be x = 0 resulting in an optimal objective function value of f(x)=4.
            However, the solver ignores constant terms and only seeks to minimize f(x) = x^2 + 2x.
            This would typically yield f(x)=0 by default with the optimal solution of x=0.
            constant_term should be set to 4 to yield an objective function value of f(x)=4.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ObjectiveAlreadySetError
            If an objective has already been set in this model.
        ValueError
            If the weights shape or the bias shape does not fit the variables in the model.
            If the weights or bias data type is not float32.

        Examples
        --------
        >>> from titanq import Model, Target
        >>> edges = {0:[4,5,6,7], 1:[4,5,6,7], 2:[4,5,6,7], 3:[4,5,6,7], 4:[0,1,2,3], 5:[0,1,2,3], 6:[0,1,2,3], 7:[0,1,2,3]}
        >>> size = len(edges)
        >>> weights = np.zeros((size, size), dtype=np.float32)
        >>> for root, connections in edges.items():
        >>>     for c in connections:
        >>>         weights[root][c] = 1
        >>> # construct the bias vector (Uniform weighting across all nodes)
        >>> bias = np.asarray([0]*size, dtype=np.float32)
        >>> model.set_objective_matrices(weights, bias, Target.MINIMIZE)
        """
        if len(self._variables) == 0:
            raise MissingVariableError("Cannot set objective before adding a variable to the model.")

        if self._objective is not None:
            raise ObjectiveAlreadySetError("An objective has already have been set for this model.")

        log.debug(f"set objective matrix and bias vector.")

        array_like_factory = ArrayLikeFactory()
        self._objective = Objective(
            var_size=len(self._variables),
            bias=array_like_factory.create(bias),
            weights=array_like_factory.create(weights),
            target=target,
            constant_term=constant_term,
        )


    def add_set_partitioning_constraints_matrix(self, constraint_mask: np.ndarray):
        """
        Adds set partitioning constraints in matrix format to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 2-D dense ndarray (must be binary).
            The constraint_mask matrix of shape (M, N) where M the number of constraints and N is the number of variables.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ConstraintSizeError
            If the constraint_mask shape does not fit the expected shape of this model.
        ValueError
            If the constraint_mask data type is not binary.

        Examples
        --------
        >>> constraint_mask = np.array([[1, 1, 1, 0, 1], [1, 1, 1, 1, 0]])
        >>> model.add_set_partitioning_constraints_matrix(constraint_mask)
        """
        if len(self._variables) == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_set_partitioning_constraints_matrix() function with a vector, " \
                "please use add_set_partitioning_constraint() instead")

        if not is_ndarray_binary(constraint_mask):
            raise ValueError(f"Cannot add a constraint if the values are not in binary.")

        self._constraints.add_constraint(
            num_variables=len(self._variables),
            constraint_weights=constraint_mask,
            constraint_bounds=np.ones((constraint_mask.shape[0],2))
        )


    def add_set_partitioning_constraint(self, constraint_mask: np.ndarray):
        """
        Adds set partitioning constraint vector to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 1-D dense ndarray (must be binary).
            The constraint_mask vector of shape (N,) where N is the number of variables.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ConstraintSizeError
            If the constraint_mask shape does not fit the expected shape of this model.
        ValueError
            If the constraint_mask data type is not binary.

        Examples
        --------
        >>> constraint_mask = np.array([1, 1, 1, 0, 1])
        >>> model.add_set_partitioning_constraint(constraint_mask)
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use this add_set_partitioning_constraint() function with a matrix, " \
                "please use add_set_partitioning_constraints_matrix() instead")

        self.add_set_partitioning_constraints_matrix(reshape_to_2d(constraint_mask))


    def add_cardinality_constraints_matrix(self, constraint_mask: np.ndarray, cardinalities: np.ndarray):
        """
        Adds cardinality constraints in matrix format to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 2-D dense ndarray (must be binary).
            The constraint_mask matrix of shape (M, N) where M the number of constraints and N is the number of variables.
        cardinalities
            A NumPy 1-D ndarray (must be non-zero unsigned integer).
            The constraint_rhs vector of shape (M,) where M is the number of constraints.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ConstraintSizeError
            If the constraint_mask shape or the constraint_rhs shape does not fit the expected shape of this model.
        ValueError
            If the constraint_mask is not binary or cardinalities data type are not unsigned integers.

        Examples
        --------
        >>> constraint_mask = np.array([[1, 1, 1, 0, 1], [1, 1, 1, 1, 0]])
        >>> cardinalities = np.array([3, 2])
        >>> model.add_cardinality_constraints_matrix(constraint_mask, cardinalities)
        """
        if len(self._variables) == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_cardinality_constraints_matrix() function with a vector, " \
                "please use add_cardinality_constraint() instead")

        if cardinalities.ndim != 1:
            raise ValueError(f"Cannot set constraints if cardinalities is not a NumPy 1-D dense ndarray")

        if not np.issubdtype(cardinalities.dtype, np.integer):
            raise ValueError("Found cardinalities data types not integer")

        if not np.all(cardinalities > 0):
            raise ValueError("Found cardinalities data types not unsigned integer")

        if not is_ndarray_binary(constraint_mask):
            raise ValueError(f"Cannot add a constraint if the values are not in binary.")

        if cardinalities.shape[0] != constraint_mask.shape[0]:
            raise ValueError(
                f"Cannot set constraints if cardinalities shape is not the same as the expected shape of this model." \
                f" Got cardinalities shape: {cardinalities.shape[1]}, constraint mask shape: {constraint_mask.size()}.")

        validate_cardinalities(constraint_mask, cardinalities)

        self._constraints.add_constraint(
            num_variables=len(self._variables),
            constraint_weights=constraint_mask,
            constraint_bounds=np.repeat(cardinalities, 2).reshape(-1, 2)
        )


    def add_cardinality_constraint(self, constraint_mask: np.ndarray, cardinality: int):
        """
        Adds cardinality constraint vector to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 1-D dense ndarray (must be binary).
            The constraint_mask vector of shape (N,) where N is the number of variables.
        cardinality
            The constraint_rhs cardinality.
            This value has to be a non-zero unsigned integer.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ConstraintSizeError
            If the constraint_mask shape or the constraint_rhs shape does not fit
            the expected shape of this model.
        ValueError
            If the constraint_mask is not in binary or the cardinality is not an unsigned integer.

        Examples
        --------
        >>> constraint_mask = np.array([1, 1, 1, 0, 1])
        >>> cardinality = 3
        >>> model.add_cardinality_constraint(constraint_mask, cardinality)
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use add_cardinality_constraint() function with a matrix, " \
                "please use add_cardinality_constraints_matrix() instead")

        self.add_cardinality_constraints_matrix(reshape_to_2d(constraint_mask), np.full((1,), cardinality))


    def add_equality_constraints_matrix(self, constraint_mask: np.ndarray, limit: np.ndarray) -> None:
        """
        Adds an equality constraint matrix to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 2-D dense ndarray (float32).
            The constraint_mask vector of shape (M, N) where M the number of constraints and N is the number of variables.
        limit
            A NumPy 1-D array (float32).
            The limit vector of shape (M,) where M is the number of constraints.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ValueError
            If the constraint_mask shape does not fit the expected shape of this model.
            If the constraint_mask or limit contains irregular format ('NaN' or 'inf').

        Examples
        --------
        >>> constraint_mask = np.array([[-3.51, 0, 0, 0], [10, 0, 0, 0]], dtype=np.float32)
        >>> limit = np.array([2, 10], dtype=np.float32)
        >>> model.add_equality_constraints_matrix(constraint_mask, limit)
        """
        if len(self._variables) == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.dtype != np.float32 or limit.dtype != np.float32:
            raise ValueError(f"Input parameters must be float32, got Constraint mask: {constraint_mask.dtype}, Limit: {limit.dtype}")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_equality_constraint_matrix() function with a vector, " \
                "please use add_equality_constraint() instead")

        if ndarray_contains_nan_inf(constraint_mask):
            raise ValueError("Constraint mask contains NaN or inf values")

        if limit.ndim != 1:
            raise ValueError("Limit must be a NumPy 1-D array")

        if ndarray_contains_nan_inf(limit):
            raise ValueError("Limit contains NaN or inf values")

        self._constraints.add_constraint(
            num_variables=len(self._variables),
            constraint_weights=constraint_mask,
            constraint_bounds=np.repeat(limit, 2).reshape(-1, 2)
        )


    def add_equality_constraint(self, constraint_mask: np.ndarray, limit: np.float32) -> None:
        """
        Adds an equality constraint vector to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 1-D dense ndarray (float32).
            The constraint_mask vector of shape (N,) where N is the number of variables.
        limit
            Limit value to the constraint mask.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ValueError
            If the constraint_mask shape does not fit the expected shape of this model.
            If the constraint_mask or limit contains irregular format ('NaN' or 'inf').

        Examples
        --------
        >>> constraint_mask = np.array([1.05, -1.1], dtype=np.float32)
        >>> limit = -3.45
        >>> model.add_equality_constraint(constraint_mask, limit)
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use add_equality_constraint() function with a matrix, " \
                "please use add_equality_constraint_matrix() instead")

        self.add_equality_constraints_matrix(reshape_to_2d(constraint_mask), np.full((1,), limit, dtype=np.float32))


    def add_inequality_constraints_matrix(self, constraint_mask: np.ndarray, constraint_bounds: np.ndarray):
        """
        Adds inequality constraint matrix to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 2-D dense ndarray (float32).
            The constraint_mask vector of shape (M, N) where N is the number of variables.
        constraint_bounds
            A NumPy 2-D ndarray (float32).
            Vector of shape (M, 2) where M is the number of constraints.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ValueError
            If the constraint_mask shape does not fit the expected shape of this model.
            If the constraint_mask contains irregular format ('NaN' or 'inf').
            If the lowerbound is equal or higher than its given upperbound.

        Examples
        --------
        >>> constraint_mask = np.array([[-3.51, 0], [10, 0]], dtype=np.float32)
        >>> constraint_bounds = np.array([[8, 9], [np.nan, 100_000]], dtype=np.float32)
        >>> model.add_inequality_constraints_matrix(constraint_mask, constraint_bounds)
        """
        if len(self._variables) == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        if constraint_mask.dtype != np.float32 or constraint_bounds.dtype != np.float32:
            raise ValueError(f"Input parameters must be float32, got Constraint mask: {constraint_mask.dtype}, Limit: {constraint_bounds.dtype}")

        if constraint_mask.ndim == 1:
            raise ValueError(
                "Cannot use add_inequality_constraint_matrix() function with a vector, " \
                "please use add_inequality_constraint() instead")

        if ndarray_contains_nan_inf(constraint_mask):
            raise ValueError("Constraint mask contains NaN or inf values.")

        if is_upperbound_bigger_equal_lowerbound(constraint_bounds):
            raise ValueError("Constraint bounds contains lowerbounds equal or higher than their upperbound.")

        self._constraints.add_constraint(
            num_variables=len(self._variables),
            constraint_weights=constraint_mask,
            constraint_bounds=constraint_bounds
        )


    def add_inequality_constraint(self, constraint_mask: np.ndarray, constraint_bounds: np.ndarray):
        """
        Adds inequality constraint vector to the model. At least one bound must be set.

        Parameters
        ----------
        constraint_mask
            A NumPy 1-D dense ndarray (float32).
            The constraint_mask vector of shape (N,) where N is the number of variables.
        constraint_bounds
            A NumPy 1-D ndarray (float32).
            Vector of shape (2,)

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ValueError
            If the constraint_mask shape does not fit the expected shape of this model.
            If the constraint_mask contains irregular format ('NaN' or 'inf').
            If the lowerbound is equal or higher than the upperbound.

        Examples
        --------
        >>> constraint_mask = np.array([1.05, -1.1], dtype=np.float32)
        >>> constraint_bounds = np.array([1.0, np.nan], dtype=np.float32)
        >>> model.add_inequality_constraint(constraint_mask, constraint_bounds)
        """
        if constraint_mask.ndim > 1:
            raise ValueError(
                "Cannot use add_inequality_constraint() function with a matrix, " \
                "please use add_inequality_constraint_matrix() instead")

        self.add_inequality_constraints_matrix(reshape_to_2d(constraint_mask), reshape_to_2d(constraint_bounds))


    def add_quadratic_equality_constraint(
        self,
        constraint_mask: np.ndarray,
        limit: np.float32,
        constraint_linear_weights: Optional[np.ndarray] = None
    ) -> None:
        """
        ℹ️ **This feature is experimental and may change.**

        Adds an equality quadratic constraint to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 2-D dense ndarray (float32).
            The constraint_mask vector of shape (N, N) where N is the number of variables.
        limit
            Limit value to the constraint mask.
        constraint_linear_weights
            A NumPy 1-D dense ndarray (float32).
            The constraint_linear_weights vector of shape (N,) where N is the number of variables.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ValueError
            If the constraint_mask shape does not fit the expected shape of this model.
            If the constraint_mask or limit contains irregular format ('NaN' or 'inf').

        Examples
        --------
        >>> constraint_mask = np.array([[0.1, 0.1], [0.1, 0.1]], dtype=np.float32)
        >>> limit = 1.0
        >>> constraint_linear_weights = np.array([0, 0.2], dtype=np.float32)
        >>> model.add_quadratic_equality_constraint(constraint_mask, limit, constraint_linear_weights)
        """
        self.add_quadratic_inequality_constraint(
            constraint_mask=constraint_mask,
            constraint_bounds=np.full((2,), limit, dtype=np.float32),
            constraint_linear_weights=constraint_linear_weights
        )


    def add_quadratic_inequality_constraint(
        self,
        constraint_mask: np.ndarray,
        constraint_bounds: np.ndarray,
        constraint_linear_weights: Optional[np.ndarray] = None
    ) -> None:
        """
        ℹ️ **This feature is experimental and may change.**

        Adds an inequality quadratic constraint to the model.

        Parameters
        ----------
        constraint_mask
            A NumPy 2-D dense ndarray (float32).
            The constraint_mask vector of shape (N, N) where N is the number of variables.
        constraint_bounds
            A NumPy 1-D ndarray (float32).
            Vector of shape (2,).
        constraint_linear_weights
            A NumPy 1-D dense ndarray (float32).
            The constraint_linear_weights vector of shape (N,) where N is the number of variables.

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        ValueError
            If the constraint_mask shape does not fit the expected shape of this model.
            If the constraint_mask or limit contains irregular format ('NaN' or 'inf').
            If the constraint_bounds' shape is not (2,).

        Examples
        --------
        >>> constraint_mask = np.array([[1.05, -1.1], [0, 0]], dtype=np.float32)
        >>> constraint_bounds = np.array([np.nan, 10], dtype=np.float32)
        >>> constraint_linear_weights = np.array([4.0, 4.0], dtype=np.float32)
        >>> model.add_quadratic_inequality_constraint(constraint_mask, constraint_bounds, constraint_linear_weights)
        """
        if len(self._variables) == 0:
            raise MissingVariableError("Cannot set constraints before adding a variable to the model.")

        EXPECTED_BOUNDS_SHAPE = (2,)
        if constraint_bounds.shape != EXPECTED_BOUNDS_SHAPE:
            raise ValueError(
                "Invalid constraint_bounds shape: "
                + f"expected {EXPECTED_BOUNDS_SHAPE}, got {constraint_bounds.shape}")

        if constraint_bounds[0] > constraint_bounds[1]:
            raise ValueError("Input constraint_bounds lowerbound is higher than its upperbound.")

        if constraint_mask.dtype != np.float32:
            raise ValueError(f"Input parameters must be float32, got constraint_mask: {constraint_mask.dtype}")

        if ndarray_contains_nan_inf(constraint_mask):
            raise ValueError("Input parameter constraint_mask contains NaN or inf values")

        if constraint_linear_weights is not None:
            constraint_linear_weights = reshape_to_2d(constraint_linear_weights)

            if constraint_mask.dtype != np.float32:
                raise ValueError(f"Input parameters must be float32, got Constraint linear weights: {constraint_linear_weights.dtype}")

            if ndarray_contains_nan_inf(constraint_linear_weights):
                raise ValueError("Input parameter constraint_linear_weights contains NaN or inf values")

        self._quad_constraints.add_constraint(
            num_variables=len(self._variables),
            quad_constraint_weights=constraint_mask,
            quad_constraint_bounds=reshape_to_2d(constraint_bounds),
            quad_constraint_linear_weights=constraint_linear_weights
        )


    def optimize(
        self,
        *,
        beta: List[float] = [1, 0.5, 0.33, 0.25, 0.2, 0.16, 0.14, 0.125],
        coupling_mult: float = 0.5,
        timeout_in_secs: float = 10.0,
        num_chains: int = 8,
        num_engines: int = 1,
        penalty_scaling: float = None,
        precision: Precision = Precision.AUTO,
        num_buckets: int = 10,
        optimality_gap: float = 1e-4
    ) -> OptimizeResponse:
        """
        Optimize this model. Issue a solve request and wait for it to complete.

        Notes
        -----
        All of the files used during this computation will be cleaned at the end.
        For more information on how to tune those parameters, visit

        `The tuning guide <https://docs.titanq.infinityq.io/user-guide/parameter_tuning_guide>`_

        `TitanQ API documentation <https://docs.titanq.infinityq.io/>`_

        Parameters
        ----------
        beta
            Scales the problem by this factor (inverse of temperature). Beta values can then be
            adjusted to see if a better objective function value can be obtained.
            A lower beta allows for easier escape from local minima, while a higher beta
            is more likely to respect penalties and constraints.

            `Beta values tuning guide <https://docs.titanq.infinityq.io/user-guide/parameter_tuning_guide#beta>`_

            Range: List of [0, 20000]

            Recommended values: List of [0.004...2]

            NOTE: Beta values should be provided in descending order

            >>> import numpy as np
            >>> num_chains = 8
            >>> beta = (1/(np.linspace(2, 50, num_chains, dtype=np.float32))).tolist()

        coupling_mult
            Strength of parameter that keeps multiple logical copies of variables to have the
            same ground state solution. Heuristic to be tuned for a particular problem. Small values
            of this parameter will lead to an incorrect solution while large values will take a long
            time to converge to the correct solution.

            `coupling_mult tuning guide <https://docs.titanq.infinityq.io/user-guide/parameter_tuning_guide#coupling_mult>`_

            Range: [0, 100]

            Recommended values: [0.05...1.0]

        timeout_in_secs
            Maximum time (in second) the computation can take.

            `timeout_in_secs tuning guide <https://docs.titanq.infinityq.io/user-guide/parameter_tuning_guide#timeout_in_secs>`_

            Range: [0.1, 600]

            NOTE: Currently there is no other stop criteria. All computations will run up to the
            timeout value.

        num_chains
            Number of parallel chains running computation. Only the best result of all
            chains is returned.

            `num_chains tuning guide <https://docs.titanq.infinityq.io/user-guide/parameter_tuning_guide#num_chains--num_engines>`_

            Recommended values: [8, 16, 32]

            NOTE: ``num_chains`` * ``num_engines`` cannot exceed 512

        num_engines
            Number of independent batches of chains to run the computation. The best result
            of the batch of chains in each engine is returned.

            `num_engines tuning guide <https://docs.titanq.infinityq.io/user-guide/parameter_tuning_guide#num_chains--num_engines>`_

            Range: [1, 512]

            NOTE: ``num_chains`` * ``num_engines`` cannot exceed 512

        penalty_scaling
            Scaling factor for constraint penalty violations. Increasing this value results
            in stronger constraint enforcement at the cost of increasing the odds of becoming
            trapped in local minima.

            Range: penalty_scaling > 0

            NOTE: If None, a value will be inferred from the objective function of the problem.

        precision
            Some problems may need a higher precision implementation to converge properly such
            as when problem weights exhibit a high dynamic range. This flag allows this higher
            precision (but slightly slower speed) implementation to be used when ``Precision.HIGH``
            is set. Setting ``Precision.STANDARD`` uses a medium precision perfect for general use
            and offering the best speed/efficiency. The default setting ``Precision.AUTO`` will
            inspect the problem passed in and determine which of ``Precision.AUTO`` or
            ``Precision.STANDARD`` precision to use based on internal metrics.

        num_buckets
            The buckets strategy consists in dividing the range of values of a continuous variable
            into the specified number of buckets.

            `num_buckets tuning guide <https://docs.titanq.infinityq.io/user-guide/parameter_tuning_guide#num_buckets>`_

            Range: num_buckets >= 0

            Recommended values: [1, 2, 3, ..., 9, 10, 20, 30, ..., 90, 100, 200, 300, ..., 900, 1000, ...]

            NOTE: If the value is set to '0', the solver will not use the buckets strategy.

        optimality_gap
            Defines when the solver converges and returns a solution. Basically an exit condition

        Returns
        -------
        OptimizeResponse
            Optimized response data object

        Raises
        ------
        MissingVariableError
            If no variable have been added to the model.
        MissingObjectiveError
            If no objective matrices have been added to the model.
        FailedComputationError
            If an error was returned by the solver instead of a result.
            The exception will contain the solver's error message.

        Examples
        --------
        basic solve
            >>> response = model.optimize(timeout_in_secs=60)
        multiple engine
            >>> response = model.optimize(timeout_in_secs=60, num_engines=2)
        custom values
            >>> response = model.optimize(beta=[0.1], coupling_mult=0.75, num_chains=8)
        print values
            >>> print("-" * 15, "+", "-" * 26, sep="")
            >>> print("Ising energy   | Result vector")
            >>> print("-" * 15, "+", "-" * 26, sep="")
            >>> for ising_energy, result_vector in response.result_items():
            >>>     print(f"{ising_energy: <14f} | {result_vector}")
        """
        if len(self._variables) == 0:
            raise errors.MissingVariableError("Cannot optimize before adding a variable to the model.")

        if self._objective is None:
            raise errors.MissingObjectiveError("Cannot optimize before adding an objective to the model.")

        result, metrics = self._solve(beta, coupling_mult, timeout_in_secs, num_chains, num_engines, penalty_scaling, precision, num_buckets, optimality_gap)

        return OptimizeResponse(self._variables, result, metrics)

    def _solve(
        self,
        beta: List[float],
        coupling_mult: float,
        timeout_in_secs: float,
        num_chains: int,
        num_engines: int,
        penalty_scaling: Optional[float],
        precision: Precision,
        num_buckets: int,
        optimality_gap: float
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Issue a solve request and wait for it to complete.

        Returns
        -------
        The result numpy array and the metric json object.
        """
        with self._storage_client as storage:
            storage.upload(Ftype.BIAS, self._objective.bias().to_bytes())
            if self._objective.weights() is not None:
                storage.upload(Ftype.WEIGHTS, self._objective.weights().to_bytes())
            if self._constraints.bounds() is not None and self._constraints.weights() is not None:
                storage.upload(Ftype.CONSTRAINT_BOUNDS, to_bytes(self._constraints.bounds()))
                storage.upload(Ftype.CONSTRAINT_WEIGHTS, to_bytes(self._constraints.weights()))
            storage.upload(Ftype.VARIABLE_BOUNDS, to_bytes(np.array([v.variable_bounds() for v in self._variables], dtype=np.float32)))
            if self._quad_constraints.weights() is not None and self._quad_constraints.bounds() is not None:
                storage.upload(Ftype.QUAD_CONSTRAINT_WEIGHTS, to_bytes(self._quad_constraints.weights()))
                storage.upload(Ftype.QUAD_CONSTRAINT_BOUNDS, to_bytes(self._quad_constraints.bounds()))
            if self._quad_constraints.linear_weights() is not None:
                storage.upload(Ftype.QUAD_CONSTRAINT_LINEAR_WEIGHTS, to_bytes(self._quad_constraints.linear_weights()))

            try:
                # api request
                request = api_model.SolveRequest(
                    input=storage.input(),
                    output=storage.output(),
                    parameters=api_model.Parameters(
                        timeout_in_secs=timeout_in_secs,
                        variable_types=''.join(v.vtype()._api_str() for v in self._variables),

                        beta=beta,
                        constant_term=self._objective.constant_term(),
                        coupling_mult=coupling_mult,
                        num_buckets=num_buckets,
                        num_chains=num_chains,
                        num_engines=num_engines,
                        optimality_gap=optimality_gap,
                        penalty_scaling=penalty_scaling,
                        precision=str(precision),
                    )
                )

                # adding constraint types
                if self._constraints.bounds() is not None and self._constraints.weights() is not None:
                    for mask, bounds in zip(self._constraints.weights(), self._constraints.bounds()):
                        self._manifest.add_constraint_type(get_constraint_type(mask, bounds))

                # adding manifest flags to the request
                request.input.manifest = api_model.Manifest(
                    has_set_partitioning_constraint=self._manifest.has_set_partitioning_constraint(),
                    has_cardinality_constraint=self._manifest.has_cardinality_constraint(),
                    has_equality_constraint=self._manifest.has_equality_constraint(),
                    has_inequality_constraint=self._manifest.has_inequality_constraint()
                )
            except ValidationError as ex:
                raise TypeError(f'Invalid parameter ({ ex.errors()[0]["loc"][0]}): {ex.errors()[0]["msg"]}')

            solve_response = self._titanq_client.solve(request)

            archive_file_content = storage.wait_for_result_to_be_uploaded_and_download()
            metrics_content, result_content = _extract_result_files_or_raise(
                archive_file_content,
                solve_response.computation_id)

        log.debug("Optimization completed")

        try:
            result = np.load(io.BytesIO(result_content))
        except (OSError, ValueError, EOFError, UnpicklingError) as ex:
            raise errors.UnexpectedServerResponseError(f"Failed to load result.npy zipped binaries from the solver response. Numpy error: {ex}")

        try:
            metrics = json.loads(metrics_content)
        except (TypeError, json.JSONDecodeError) as ex:
            raise errors.UnexpectedServerResponseError(f"Failed to load metrics.json zipped binaries from the solver response. JSON error: {ex}")

        return result, metrics


def _extract_result_files_or_raise(
        archive_file_content: bytes,
        computation_id: str,
    ) -> Tuple[bytes, bytes]:
    """
    Take the raw content of a zip file returned by the solver, and
    return the unzipped contents of the metrics and the result files.

    If the zip file is invalid, or if it contains an error.json instead,
    raises an exception. The computation ID will always be included
    in the error message, so that we get it when users send their
    error message.
    """

    try:
        with zipfile.ZipFile(io.BytesIO(archive_file_content), 'r') as zip_file:
            try:
                # We should always either have metrics + result files OR an error.json file
                metrics_content = zip_file.read("metrics.json")
                result_content = zip_file.read("result.npy")
            except (KeyError) as ex:
                try:
                    error_content = zip_file.read("error.json")
                    error_message = (
                        json.loads(error_content)["error"]
                        + f" (computation ID = {computation_id})")
                    raise errors.FailedComputationError(error_message)
                except (TypeError, KeyError, json.decoder.JSONDecodeError) as ex:
                    raise errors.UnexpectedServerResponseError(
                        "Unexpected response format from the solver, please contact InfinityQ support for more help" \
                        f" and provide the following computation ID: {computation_id}") from ex
    except zipfile.BadZipFile as ex:
        raise errors.UnexpectedServerResponseError(
            "Failed to open the result zip file. Please contact InfinityQ support for more help" \
            f" and provide the following computation ID: {computation_id}") from ex

    return metrics_content, result_content
