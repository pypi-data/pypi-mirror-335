# Copyright (c) 2024, InfinityQ Technology, Inc.
from datetime import datetime
from pydantic import BaseModel, Field, RootModel, field_serializer, SecretStr
from typing import List, Optional, Union


#########################
##    solve models     ##
#########################
class AwsStorage(BaseModel):
    """
    S3 backend storage
    """
    bucket_name: str
    access_key_id: SecretStr
    secret_access_key: SecretStr

    @field_serializer('access_key_id', 'secret_access_key', when_used='json')
    def dump_secret(self, v):
        return v.get_secret_value()

class Manifest(BaseModel):
    """
    The manifest object of the solver request
    """
    has_set_partitioning_constraint: bool
    has_cardinality_constraint: bool
    has_equality_constraint: bool
    has_inequality_constraint: bool

class S3Input(BaseModel):
    """
    Input object of the solve request with s3
    """
    s3: AwsStorage
    weights_file_name: Optional[str]
    bias_file_name: str
    variable_bounds_file_name: Optional[str]
    constraint_bounds_file_name: Optional[str]
    constraint_weights_file_name: Optional[str]
    quad_constraint_weights_file_name: Optional[str]
    quad_constraint_bounds_file_name: Optional[str]
    quad_constraint_linear_weights_file_name: Optional[str]

    manifest: Optional[Manifest]


class UrlInput(BaseModel):
    """
    Input object of the solve request with url
    """
    # always true, the user does not have to set this value
    file_name_is_url: bool = Field(default=True, frozen=True)
    weights_file_name: Optional[str]
    bias_file_name: str
    variable_bounds_file_name: Optional[str]
    constraint_weights_file_name: Optional[str]
    constraint_bounds_file_name: Optional[str]
    quad_constraint_weights_file_name: Optional[str]
    quad_constraint_bounds_file_name: Optional[str]
    quad_constraint_linear_weights_file_name: Optional[str]
    manifest: Optional[Manifest]


class S3Output(BaseModel):
    """
    Output object of the solve request with s3
    """
    result_archive_file_name: str
    s3: AwsStorage

class UrlOutput(BaseModel):
    """
    Output object of the solve request with url
    """
    # always true, the user does not have to set this value
    file_name_is_url: bool = Field(default=True, frozen=True)
    result_archive_file_name: str


class Parameters(BaseModel):
    """
    Tuning parameters used by the solver
    """
    timeout_in_secs: float
    variable_types: str

    beta: List[float]
    constant_term: float
    coupling_mult: float
    num_buckets: int
    num_chains: int
    num_engines: int
    optimality_gap: float
    penalty_scaling: Optional[float]
    precision: str


class SolveRequest(BaseModel):
    """
    The actual solve request object send to the backend
    """
    input: Union[S3Input, UrlInput]
    output: Union[S3Output, UrlOutput]
    parameters: Parameters


class SolveResponse(BaseModel):
    """
    The response object returned by the backend on solve request
    """
    computation_id: str
    status: str
    message: str


#########################
##   credits models    ##
#########################
class CreditDetails(BaseModel):
    credits: int
    start_date: datetime
    expiration_date: datetime
class CreditsResponse(RootModel[List[CreditDetails]]):
    """
    The response object returned by the backend on credits request
    """
    pass



#########################
## temp_storage models ##
#########################
class FileUrls(BaseModel):
    """
    Object always containing a pair of a download and an upload url
    """
    download: str
    upload: str


class TempStorageInput(BaseModel):
    """
    Object containing input files for temporary storage object
    """
    weights_file: FileUrls = Field(alias="weights")
    bias_file: FileUrls = Field(alias="bias")
    variable_bounds_file: FileUrls = Field(alias="variable_bounds")
    constraint_weights_file: FileUrls = Field(alias="constraint_weights")
    constraint_bounds_file: FileUrls = Field(alias="constraint_bounds")
    quad_constraint_weights_file: FileUrls = Field(alias="quad_constraint_weights")
    quad_constraint_bounds_file: FileUrls = Field(alias="quad_constraint_bounds")
    quad_constraint_linear_weights_file: FileUrls = Field(alias="quad_constraint_linear_weights")


class TempStorageOutput(BaseModel):
    """"
    Object containing output files for temporary storage object
    """
    result_archive_file: FileUrls = Field(alias="result")


class TempStorageResponse(BaseModel):
    """
    The response object returned by the backend on temporary storage response
    """
    input: TempStorageInput
    output: TempStorageOutput
