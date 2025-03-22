# Copyright (c) 2024, InfinityQ Technology, Inc.
from enum import Enum
import io
import numpy as np

from abc import ABC, abstractmethod
from typing import Optional, Union

from .._client.model import S3Input, S3Output, UrlInput, UrlOutput

class Ftype(Enum):
    WEIGHTS= "weights"
    BIAS = "bias"
    VARIABLE_BOUNDS= "variable_bounds"
    CONSTRAINT_BOUNDS = "constraint_bounds"
    CONSTRAINT_WEIGHTS = "constraints_weights"
    QUAD_CONSTRAINT_WEIGHTS = "quad_constraint_weights"
    QUAD_CONSTRAINT_BOUNDS = "quad_constraint_bounds"
    QUAD_CONSTRAINT_LINEAR_WEIGHTS = "quad_constraint_linear_weights"
    RESULT = "result"


class StorageClient(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def __enter__(self):
        return self

    @abstractmethod
    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    @abstractmethod
    def input(self) -> Union[S3Input, UrlInput]:
        """
        Returns the api model for the input of the solve request

        :return: either the s3 or the url input
        """

    @abstractmethod
    def output(self) -> Union[S3Output, UrlOutput]:
        """
        Returns the api model for the output of the solve request

        :return: either the s3 or the url output
        """

    @abstractmethod
    def upload(self, file_type: Ftype, data: bytes):
        """Uploads .npy arrays to the storage client"""

    @abstractmethod
    def wait_for_result_to_be_uploaded_and_download(self) -> bytes:
        """
        Wait until a file is uploaded on the storage client and download it

        :return: content of the result file in bytes
        """

def to_bytes(array: Optional[np.ndarray]) -> Optional[bytes]:
        """
        :return: numpy array as bytes
        """
        if array is None:
            return None

        buffer = io.BytesIO()
        np.save(buffer, array)
        return buffer.getvalue()