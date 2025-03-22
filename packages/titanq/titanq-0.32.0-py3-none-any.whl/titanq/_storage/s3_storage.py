# Copyright (c) 2024, InfinityQ Technology, Inc.
import datetime
from io import BytesIO
from itertools import chain
import boto3
import boto3.s3
import boto3.s3.transfer
import botocore
import logging
import time

from .._client.model import AwsStorage, S3Input, S3Output
from .storage_client import Ftype, StorageClient

log = logging.getLogger("TitanQ")

_TRANSFER_CONFIG = boto3.s3.transfer.TransferConfig(
    multipart_chunksize=5 * 1024 * 1024, # 5 MB
    multipart_threshold=5 * 1024 * 1024, # 5 MB
)

class S3Storage(StorageClient):
    """Storage client using S3 bucket from AWS"""
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket_name: str,
    ) -> None:
        """
        Initiate the S3 bucket client for handling temporary files.

        Parameters
        ----------
        access_key
            Used to upload and download files from an AWS S3 bucket.
        secret_key
            Used to upload and download files from an AWS S3 bucket.
        bucket_name
            Name of the AWS S3 bucket used to store temporarily data that the TitanQ optimizer will read.

        Raises
        ------
        botocore.exceptions.ParamValidationError
            If any AWS argument is missing this will raise an exception.

        Examples
        --------
        >>> storage_client = S3Storage(
        >>>     access_key="{insert aws bucket access key here}",
        >>>     secret_key="{insert aws bucket secret key here}",
        >>>     bucket_name="{insert bucket name here}"
        >>> )
        """
        self._s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        self._access_key_id = access_key
        self._secret_access_key = secret_key
        self._bucket_name = bucket_name

        timestamp = datetime.datetime.now().isoformat()
        self._remote_folder = f"titanq_sdk/{timestamp}"

        # keep track of which file were uploaded
        self._file_uploaded = set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._delete_remote_object()

    def upload(self, file_type: Ftype, data: bytes):
        # check if the file type is one that can be uploaded. if so, do so
        if file_type not in (Ftype.WEIGHTS,
                         Ftype.BIAS,
                         Ftype.VARIABLE_BOUNDS,
                         Ftype.CONSTRAINT_WEIGHTS,
                         Ftype.CONSTRAINT_BOUNDS,
                         Ftype.QUAD_CONSTRAINT_WEIGHTS,
                         Ftype.QUAD_CONSTRAINT_BOUNDS,
                         Ftype.QUAD_CONSTRAINT_LINEAR_WEIGHTS,):
            raise NotImplementedError(f"File type {file_type} not supported for upload")

        filename = self._get_full_filename(file_type.value)

        log.debug(f"Uploading object on AWS s3: {filename}")
        temp_file = BytesIO(data)
        self._s3.upload_fileobj(temp_file, Bucket=self._bucket_name, Key=filename, Config=_TRANSFER_CONFIG)
        self._file_uploaded.add(filename)


    def input(self) -> S3Input:
        weights = self._get_full_filename(Ftype.WEIGHTS.value)
        variable_bounds = self._get_full_filename(Ftype.VARIABLE_BOUNDS.value)
        constraint_weights = self._get_full_filename(Ftype.CONSTRAINT_WEIGHTS.value)
        constraint_bounds = self._get_full_filename(Ftype.CONSTRAINT_BOUNDS.value)
        quad_constraint_weights = self._get_full_filename(Ftype.QUAD_CONSTRAINT_WEIGHTS.value)
        quad_constraint_bounds = self._get_full_filename(Ftype.QUAD_CONSTRAINT_BOUNDS.value)
        quad_constraint_linear_weights = self._get_full_filename(Ftype.QUAD_CONSTRAINT_LINEAR_WEIGHTS.value)

        return S3Input(
            s3=self._get_api_model_location(),
            weights_file_name=weights if weights in self._file_uploaded else None,
            bias_file_name=self._get_full_filename(Ftype.BIAS.value),
            variable_bounds_file_name=variable_bounds if variable_bounds in self._file_uploaded else None,
            constraint_weights_file_name=constraint_weights if constraint_weights in self._file_uploaded else None,
            constraint_bounds_file_name=constraint_bounds if constraint_bounds in self._file_uploaded else None,
            quad_constraint_weights_file_name=quad_constraint_weights if quad_constraint_weights in self._file_uploaded else None,
            quad_constraint_bounds_file_name=quad_constraint_bounds if quad_constraint_bounds in self._file_uploaded else None,
            quad_constraint_linear_weights_file_name=quad_constraint_linear_weights if quad_constraint_linear_weights in self._file_uploaded else None,
            manifest=None
        )

    def output(self) -> S3Output:
        return S3Output(
            result_archive_file_name=self._get_full_filename(Ftype.RESULT.value),
            s3=self._get_api_model_location())

    def _get_api_model_location(self) -> AwsStorage:
        """
        :return: An AwsStorage object that can be used in the api_model using this S3 credentials
        """
        return AwsStorage(
            bucket_name=self._bucket_name,
            access_key_id=self._access_key_id,
            secret_access_key=self._secret_access_key,
        )

    def wait_for_result_to_be_uploaded_and_download(self) -> bytes:
        result_file = self._get_full_filename(Ftype.RESULT.value)
        self._wait_for_file_to_be_uploaded(result_file)
        return self._download_file(result_file)

    def _wait_for_file_to_be_uploaded(self, filename: str):
        """
        Wait until a file exist in a bucket. It also verifies if the
        file is bigger than 0 bytes, this will ensure not downloading
        the empty archive file uploaded to test credentials

        :param filename: The full path of the file that is uploaded
        """
        log.debug(f"Waiting until object get upload on AWS s3: {filename}")
        while True:
            try:
                # check if file exist in the s3 bucket
                response = self._s3.head_object(
                    Bucket=self._bucket_name,
                    Key=filename,
                )
                # check if file content_length > 0
                if response['ContentLength'] > 0:
                    break
            except botocore.exceptions.ClientError as ex:
                # if the error we got is not 404, This is an unexpected error. Raise it
                if int(ex.response['Error']['Code']) != 404:
                    raise

            time.sleep(0.25) # wait 0.25 sec before trying again

    def _download_file(self, filename) -> bytes:
        """
        Download file from remote s3 bucket

        :param filename: The full path of the file to be uploaded

        :return: content of the file
        """
        log.debug(f"Downloading object from AWS s3: {filename}")
        object = self._s3.get_object(Bucket=self._bucket_name, Key=filename)
        return object['Body'].read()

    def _delete_remote_object(self):
        """
        Delete remote object on AWS s3

        :param key: object name to be deleted on the remote s3 bucket
        """
        for file_name in chain(self._file_uploaded, [self._get_full_filename(Ftype.RESULT.value)]):
            log.debug(f"Deleting object on AWS s3: {file_name}")
            self._s3.delete_object(Bucket=self._bucket_name, Key=file_name)

    def _get_full_filename(self, filename: str) -> str:
        return f"{self._remote_folder}/{filename}"
