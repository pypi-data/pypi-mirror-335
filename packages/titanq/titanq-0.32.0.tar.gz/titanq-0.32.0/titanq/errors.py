# Copyright (c) 2024, InfinityQ Technology, Inc.

"""
Errors specific to the TitanQ SDK.
"""

class TitanqError(Exception):
    """Base TitanQ error"""

class InvalidUrl(TitanqError):
    """API URL is not valid or accessible"""

class UnexpectedServerResponseError(TitanqError):
    """Response from the TitanQ server is not as expected"""

class MissingTitanqApiKey(TitanqError):
    """TitanQ Api key is missing"""

class MissingVariableError(TitanqError):
    """Variable has not already been registered"""

class VariableAlreadyExist(TitanqError):
    """Variable with the same name already exist"""

class MissingObjectiveError(TitanqError):
    """Objective has not already been registered"""

class ConstraintSizeError(TitanqError):
    """Unexpected number of constraints"""

class ConstraintAlreadySetError(TitanqError):
    """A constraint has already been set"""

class ObjectiveAlreadySetError(TitanqError):
    """An objective has already been set"""

class FailedComputationError(TitanqError):
    """
    The computation failed and TitanQ returned an error instead of a
    solver result.
    This exception will contain the error information from the solver.
    """

class ServerError(TitanqError):
    """Unexpected condition prevented the TitanQ server to fulfill the request"""

class ConnectionError(TitanqError):
    """Error due to a connection issue with an external resource"""

class UnsolvableRequestError(TitanqError):
    """TitanQ cannot solve this combination of parameters"""

    def __init__(self, message="TitanQ cannot solve this combination of parameters", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class TautologicalExpressionError(TitanqError):
    """
    Exception raised when an expression is tautological (always true).

    This exception indicates that the provided expression is redundant
    and does not add meaningful constraints or information.
    """
    def __init__(self, message="The provided expression is tautological and always evaluates to True, regardless of the variable values.", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class ContradictoryExpressionError(TitanqError):
    """
    Exception raised when an expression is contradictory (always false).

    This exception indicates that the provided expression is invalid
    as it represents an impossible condition.
    """
    def __init__(self, message="The provided expression is contradictory and always evaluates to False, regardless of the variable values.", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class MpsParsingError(TitanqError):
    """Base class for any error related to the MPS files parsing module"""

class MpsConfiguredModelError(MpsParsingError):
    """Passed model is already configured"""

class MpsMissingValueError(MpsParsingError):
    """A required value is missing"""

class MpsMissingSectionError(MpsParsingError):
    """A required section is missing"""

class MpsMalformedFileError(MpsParsingError):
    """The file is malformed"""

class MpsUnexpectedValueError(MpsParsingError):
    """Found an unexpected value"""

class MpsUnsupportedError(MpsParsingError):
    """Found an unsupported value"""

class ClientError(TitanqError):
    """Base client-side http error"""

class NotEnoughCreditsError(ClientError):
    """Not enough credits left"""

    def __init__(self, message="Not enough credits left", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class BadRequest(ClientError):
    """The request sent to TitanQ is not valid"""