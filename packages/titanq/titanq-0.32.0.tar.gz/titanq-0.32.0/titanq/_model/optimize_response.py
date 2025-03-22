# Copyright (c) 2024, InfinityQ Technology, Inc.
"""
``OptimizeResponse`` data object that is returned from the model when optimizing a problem.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid
import warnings

import numpy as np

from titanq import errors

from .variables import Variable

log = logging.getLogger('TitanQ')

class OptimizeResponse:
    """
    Object containing the optimization results and all of the metrics returned by the solver.
    """
    def __init__(self, variables: List[Variable], result_array: np.ndarray, metrics: Dict[str, Any]) -> None:

        # extract all the result for each given variable
        # The result array is a 2d array where each line is a different result of the same problem
        result_by_variable: Dict[str, List[List[float]]] = {}
        for variable in variables:
            name = variable.parent_name()

            if name not in  result_by_variable:
                # if variable is not yet in the dict, create empty 2d list
                result_by_variable[name] = [[] for _ in range(len(result_array))]

            for result_index, full_result in enumerate(result_array):
                result_by_variable[name][result_index].append(full_result[variable.problem_index()])


        self._result_by_variable = {k: np.array(v, dtype=np.float32) for k, v in result_by_variable.items()}
        self._metrics = metrics
        self._all_results = result_array


    def __getattr__(self, attr: str):
        # if attribute is the name of a variable
        try:
            return self._result_by_variable[attr]
        except KeyError:
            pass

        # This is to keep compatibility with older version of SDK
        if attr == "ising_energy":
            try:
                return self.__getattr__("solutions_objective_value")
            except (AttributeError, KeyError):
                pass


        warnings.warn(
            'Obtaining metrics directly as an attribute is deprecated. Use computation_metrics() or original_input_params() instead.',
            DeprecationWarning,
            stacklevel=2
        )


        # check inside computation metrics and original params for the attribute
        try:
            return self.computation_metrics(attr)
        except KeyError:
            pass

        try:
            return self.original_input_params(attr)
        except KeyError:
            pass

        # was not found, try the older behavior
        try:
            return self._metrics[attr]
        except KeyError:
            raise AttributeError(attr)


    def result_vector(self) -> np.ndarray:
        """
        The result vector

        Returns
        -------
        The result vector of this optimization.
        """
        return self._all_results


    def result_items(self) -> List[Tuple[float, np.ndarray]]:
        """
        ex. [(-10000, [0, 1, 1, 0]), (-20000, [1, 0, 1, 0]), ...]

        Returns
        -------
        List of tuples containing the solutions objective value and its corresponding result vector
        """

        solutions_objective_value = self.ising_energy
        return [(solutions_objective_value[i], self._all_results[i]) for i in range(len(self._all_results))]


    def computation_id(self) -> uuid.UUID:
        """
        The computation id is a Universal unique id that identify this computation inside the TitanQ platform.

        Provide this id on any support request to the InfinityQ.

        Returns
        -------
        The computation id of this solve.

        Raises
        ------
        UnexpectedServerResponseError
            The server response doesn't contain a computation id
        """
        try:
            computation_id = self._metrics['computation_id']
        except KeyError as ex:
            raise errors.UnexpectedServerResponseError(f"Failed to fetch '{ex}' from the metrics response file, please contact InfinityQ support for more help")

        return computation_id


    def computation_metrics(self, key: str = None) -> Any:
        """
        The computation metrics the solver returns

        Returns
        -------
        All computation metrics if no key is given of the specific metrics with the associated key if one is provided.

        Raises
        ------
        UnexpectedServerResponseError
            The server response doesn't contain the computation metrics or the passed key
        """
        try:
            metrics = self._metrics['computation_metrics']
            if key:
                metrics = metrics[key]
        except KeyError as ex:
            raise errors.UnexpectedServerResponseError(f"Failed to fetch '{ex}' from the metrics response file, please contact" \
                f" InfinityQ support for more help and provide the following computation ID: {self.computation_id()}") from ex

        return metrics


    def parameters_used(self, key: str = None) -> Any:
        """
        The actual parameters used by the solver. If a parameter was not used, the value will be set to None.

        Returns
        -------
        The parameters used by the solver

        Raises
        ------
        UnexpectedServerResponseError
            The server response doesn't contain the parameters used or the passed key
        """
        try:
            metrics = self._metrics['parameters_used']
            if key:
                metrics = metrics[key]
        except KeyError as ex:
            raise errors.UnexpectedServerResponseError(f"Failed to fetch '{ex}' from the metrics response file, please contact" \
                f" InfinityQ support for more help and provide the following computation ID: {self.computation_id()}") from ex

        return metrics


    def problem_shape(self, key: str = None) -> Any:
        """
        The problem shape analyzed by the solver

        Returns
        -------
        The problem shape

        Raises
        ------
        UnexpectedServerResponseError
            The server response doesn't contain the problem shape or the passed key
        """
        try:
            metrics = self._metrics['problem_shape']
            if key:
                metrics = metrics[key]
        except KeyError as ex:
            raise errors.UnexpectedServerResponseError(f"Failed to fetch '{ex}' from the metrics response file, please contact" \
                f" InfinityQ support for more help and provide the following computation ID: {self.computation_id()}") from ex

        return metrics


    def solver_used(self) -> str:
        """
        The solver class used for the computation

        Returns
        -------
        The solver class used

        Raises
        ------
        UnexpectedServerResponseError
            The server response doesn't contain the solver used
        """
        try:
            solver_used = self._metrics['solver_used']
        except KeyError as ex:
            raise errors.UnexpectedServerResponseError(f"Failed to fetch '{ex}' from the metrics response file, please contact" \
                f" InfinityQ support for more help and provide the following computation ID: {self.computation_id()}") from ex

        return solver_used


    def constraint_violations(self) -> Tuple[Optional[List[int]], Optional[List[List[int]]]]:
        """
        Obtain constraint violations for each engine (``num_engines``).
        If no constraints were used in the computation, the values will be None.

        Return
        ------
        A tuple of two lists
        - First list indicate the total number of constraint violations for each engine
        - Second list contains a list of the constraint violation indexes for each engine

        """
        return (
            self.computation_metrics("total_constraint_violations"),
            self.computation_metrics("constraint_violation_indices")
        )


    def total_number_of_constraints(self) -> int:
        """
        Returns the number of constraints passed to the solver for the computation.

        Returns
        -------
        The number of constraints, or 0 if no constraints were defined in the request.
        """
        constraint_weights_shape: Tuple[int, int] = self.original_input_params("constraint_weights_shape")

        return 0 if constraint_weights_shape is None else constraint_weights_shape[0]


    def original_input_params(self, key: str = None) -> Any:
        """
        .. deprecated:: 0.29.0
            Use parameters_used() instead.

        The original input params sent to the solver

        Returns
        -------
        All original params if no key is given. A specific param with the associated key if one is provided.

        Raises
        ------
        UnexpectedServerResponseError
            The server response doesn't contain the original input parameters or the passed key
        """
        try:
            metrics = self._metrics['original_input_params']
            if key:
                metrics = metrics[key]
        except KeyError as ex:
            raise errors.UnexpectedServerResponseError(f"Failed to fetch '{ex}' from the metrics response file, please contact" \
                f" InfinityQ support for more help and provide the following computation ID: {self.computation_id()}") from ex

        return metrics


    def metrics(self, key: str = None) -> Union[str, Dict[str, Any]]:
        """
        .. deprecated:: 0.7.0
            Use computation_metrics() or original_input_params() instead.

        Returns
        -------
        All metrics if no key is given. A specific metric with the associated key if one is provided.

        Raises
        ------
        UnexpectedServerResponseError
            The server response doesn't contain the metrics or the passed key
        """
        warnings.warn(
            'Calling metrics() is deprecated. Use computation_metrics() or original_input_params() instead.',
            DeprecationWarning,
            stacklevel=2
        )
        if key:
            try:
                metrics = metrics[key]
            except KeyError as ex:
                raise errors.UnexpectedServerResponseError(f"Failed to fetch '{ex}' from the solver response, please contact" \
                f" InfinityQ support for more help and provide the following computation ID: {self.computation_id()}") from ex

            return metrics
        else:
            return self._metrics