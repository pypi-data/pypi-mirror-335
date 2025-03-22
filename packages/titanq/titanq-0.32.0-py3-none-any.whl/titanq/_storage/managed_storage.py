# Copyright (c) 2024, InfinityQ Technology, Inc.
import logging
import requests
import time
import urllib3

from .._client.model import UrlInput, UrlOutput
from .storage_client import Ftype, StorageClient
from .._client.client import Client
from ..errors import ConnectionError

log = logging.getLogger("TitanQ")


class ManagedStorage(StorageClient):
    def __init__(self, titanq_client: Client):
        """
        Initiate the managed storage client for handling the temporary files.

        :titanq_client: titanq_client to be used to fetch temporary URL's
        """
        self._titanq_client = titanq_client
        self._urls = None
        self._initialize_upload_status()
        self._session = None

    def __enter__(self):
        self._initialize_upload_status()

        self._session = requests.Session()
        retries = urllib3.Retry(
                    total=3,
                    backoff_factor=0.5,
                    status_forcelist=[502, 503, 504, 495],
                )
        self._session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))

        self._urls = self._titanq_client.temp_storage()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._delete_remote_object()
        if self._session: self._session.close()

    def upload(self, file_type: Ftype, data: bytes):
        url, has_a_flag_to_set = {
            Ftype.WEIGHTS: (self._urls.input.weights_file.upload, True),
            Ftype.BIAS: (self._urls.input.bias_file.upload, False),
            Ftype.VARIABLE_BOUNDS: (self._urls.input.variable_bounds_file.upload, True),
            Ftype.CONSTRAINT_BOUNDS: (self._urls.input.constraint_bounds_file.upload, True),
            Ftype.CONSTRAINT_WEIGHTS: (self._urls.input.constraint_weights_file.upload, True),
            Ftype.QUAD_CONSTRAINT_WEIGHTS: (self._urls.input.quad_constraint_weights_file.upload, True),
            Ftype.QUAD_CONSTRAINT_BOUNDS: (self._urls.input.quad_constraint_bounds_file.upload, True),
            Ftype.QUAD_CONSTRAINT_LINEAR_WEIGHTS: (self._urls.input.quad_constraint_linear_weights_file.upload, True),

        }.get(file_type, (None, None))

        if url:
            log.debug(f"Uploading file ({file_type.value}) to temporary storage")
            self._session.put(url, data=data)
            if has_a_flag_to_set and file_type in self._file_upload_status:
                self._file_upload_status[file_type] = True
        else:
            raise NotImplementedError(f"File type {file_type} not supported for upload")

    def input(self) -> UrlInput:
        return UrlInput(
            weights_file_name=self._urls.input.weights_file.download if self._file_upload_status[Ftype.WEIGHTS] else None,
            bias_file_name=self._urls.input.bias_file.download,
            variable_bounds_file_name=self._urls.input.variable_bounds_file.download if self._file_upload_status[Ftype.VARIABLE_BOUNDS] else None,
            constraint_weights_file_name=self._urls.input.constraint_weights_file.download if self._file_upload_status[Ftype.CONSTRAINT_WEIGHTS] else None,
            constraint_bounds_file_name=self._urls.input.constraint_bounds_file.download if self._file_upload_status[Ftype.CONSTRAINT_BOUNDS] else None,
            quad_constraint_weights_file_name=self._urls.input.quad_constraint_weights_file.download if self._file_upload_status[Ftype.QUAD_CONSTRAINT_WEIGHTS] else None,
            quad_constraint_bounds_file_name=self._urls.input.quad_constraint_bounds_file.download if self._file_upload_status[Ftype.QUAD_CONSTRAINT_BOUNDS] else None,
            quad_constraint_linear_weights_file_name=self._urls.input.quad_constraint_linear_weights_file.download if self._file_upload_status[Ftype.QUAD_CONSTRAINT_LINEAR_WEIGHTS] else None,
            manifest=None
        )

    def output(self) -> UrlOutput:
        return UrlOutput(result_archive_file_name=self._urls.output.result_archive_file.upload)

    def wait_for_result_to_be_uploaded_and_download(self) -> bytes:
        """
        Wait until the content of the file in the temporary storage is bigger
        than 0 bytes. Meaning it will wait until the file is uploaded

        :param url: Url to download the file.
        """
        retries = 0
        while retries < 5:
            try:
                response = self._session.get(self._urls.output.result_archive_file.download)
                response.raise_for_status()
                if len(response.content) > 0:
                    return response.content

            except (urllib3.exceptions.ProtocolError, requests.exceptions.ConnectionError, ConnectionResetError) as e:
                retries = retries + 1
                log.warning(f"Caught error {e} [retries: {retries}]")
                time.sleep(1.0)

            time.sleep(0.25)

        raise ConnectionError("Unexpected error with InfinityQ internal storage, please contact InfinityQ support for more information")

    def _delete_remote_object(self) -> None:
        log.debug("Temporary storage option does not delete any file at the moment")

    def _initialize_upload_status(self):
        """Initializes or resets the upload status dictionary."""
        self._file_upload_status = {
            Ftype.WEIGHTS: False,
            Ftype.VARIABLE_BOUNDS: False,
            Ftype.CONSTRAINT_WEIGHTS: False,
            Ftype.CONSTRAINT_BOUNDS: False,
            Ftype.QUAD_CONSTRAINT_WEIGHTS: False,
            Ftype.QUAD_CONSTRAINT_BOUNDS: False,
            Ftype.QUAD_CONSTRAINT_LINEAR_WEIGHTS: False,
        }
