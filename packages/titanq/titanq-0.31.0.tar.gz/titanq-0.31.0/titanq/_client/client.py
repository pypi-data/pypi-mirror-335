# Copyright (c) 2024, InfinityQ Technology, Inc.
import logging
import os
import requests

from pydantic import BaseModel, ValidationError
from typing import Any, Dict, Optional, Type
from urllib.parse import urljoin

import requests.adapters
import urllib3

from .model import CreditsResponse, SolveRequest, SolveResponse, TempStorageResponse
from titanq import errors


log = logging.getLogger("TitanQ")

_QUEUED_STATUS = "Queued"
_TITANQ_API_VERSION = "v1"
_USER_AGENT_HEADER = 'User-Agent'

class Client:
    """
    TitanQ api client is a simple wrapper around TitanQ api to help interact with the
    service without the need to deal with http request
    """
    def __init__(self, api_key: Optional[str], base_server_url: str) -> None:
        api_key = api_key or os.getenv("TITANQ_API_KEY")
        if api_key is None:
            raise errors.MissingTitanqApiKey(
                "No API key is provided. You can set your API key in the Model, "
                + "or you can set the environment variable TITANQ_API_KEY")
        self._server_url = base_server_url
        self._api_key = api_key


    def temp_storage(self) -> TempStorageResponse:
        """
        Query temporary storage url's

        :return: The temporary storage response

        :raises requests.exceptions.HTTPError: If an unexpected Error occur during request.
        """
        return self._do_http_request(f"{_TITANQ_API_VERSION}/temp_storage", response_type=TempStorageResponse)

    def credits(self) -> CreditsResponse:
        """
        Query Amount of credits remaining

        :return: The credit response.

        :raises requests.exceptions.HTTPError: If an unexpected Error occur during request.
        """
        return self._do_http_request(f"{_TITANQ_API_VERSION}/credits", response_type=CreditsResponse)

    def solve(self, request: SolveRequest) -> SolveResponse:
        """
        Issue a new solve request to the backend

        :param request: The solve request to issue to the solver

        :return: The response to the solve request (Not the response of the computation)
        """
        log.debug(f"Issuing solve request to TitanQ server ({self._server_url}): {request}")
        response = self._do_http_request(f"{_TITANQ_API_VERSION}/solve", body=request, method='POST', response_type=SolveResponse)

        log.debug(f"Solve request response: {response}")
        return response


    def _do_http_request(
            self,
            path: str,
            *,
            headers: Dict[str, str] = {},
            body: BaseModel = None,
            method='GET',
            response_type: Type[BaseModel]
        ) -> Any:
        """
        Execute the actual http request to the TitanQ api while adding all defaults params

        :param headers: non-default header to the request.
        :param body: Body of the request.
        :param method: Which http method to use while performing the request.
        :param response_type: The object class that the json response will be cast to.

        :raise errors.TitanqError | NotImplementedError: If the request cannot be fulfilled in any way

        :return: The response object created from the json response of the http request.
        """
        headers['authorization'] = self._api_key
        headers[_USER_AGENT_HEADER] = self._user_agent_string()
        url = urljoin(self._server_url, path)
        with requests.Session() as session:
            retries = urllib3.Retry(
                        total=3,
                        backoff_factor=0.5,
                        status_forcelist=[502, 503, 504, 495],
                        allowed_methods={"POST", "GET"},
                    )
            session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
            method = method.upper()

            try:
                if method=='GET':
                    response = session.get(url, headers=headers)
                elif method=='POST':
                    response = session.post(url, headers=headers, data=body.model_dump_json())
                else:
                    raise NotImplementedError(f"Tried to call the TitanQ server with an unknown http method: {method}")
            except requests.exceptions.MissingSchema:
                raise errors.InvalidUrl(f"Invalid TitanQ server URL '{self._server_url}'. Did you mean https://{self._server_url}?")
            except (requests.exceptions.InvalidURL, requests.exceptions.ConnectionError):
                raise errors.InvalidUrl(f"Cannot find a TitanQ server at this URL '{self._server_url}'")
            except Exception as ex:
                raise errors.BadRequest(f"Failed to send a request to the TitanQ server: {ex}")

            self._raise_for_status(response, response_type)

            return self._parse_json(response_type, response.content)


    def _user_agent_string(self) -> str:
        from titanq import __version__ as titanq_version # importing current module without cycle

        request_user_agent = requests.utils.default_headers().get(_USER_AGENT_HEADER, '')
        titanq_user_agent = f"TitanQ-sdk/{titanq_version} " + request_user_agent
        return titanq_user_agent.rstrip()

    def _parse_json(self, json_model, json_string):
        """Create the response object from the response body

        :param json_model: Pydantic model
        :param json_string: JSON string to be parsed as a model instance
        :raises errors.UnexpectedServerResponseError: If JSON string doesn't match model
        :return: response object from the body
        """
        try:
            return json_model.model_validate_json(json_string)
        except ValidationError:
            raise errors.UnexpectedServerResponseError(f"Failed to parse the response from the TitanQ server. The raw response is: {json_string}")

    def _raise_for_status(self, response: requests.Response, response_type):
        """ Raise the right error type depending on the status code of the response passed

        :raises errors.TitanqError: According to the status code
        """
        reason = ""
        try:
            res = self._parse_json(response_type, response.content)
            reason = res.message
        except (AttributeError, errors.UnexpectedServerResponseError):
            # We don't have a solver error message. The HTTP error message will be shown if an error is raised.
            pass

        if response.reason and not reason:
            reason = response.reason

        if 100 <= response.status_code < 400:
            return
        elif 400 == response.status_code:
            raise errors.BadRequest(reason)
        elif 402 == response.status_code:
            raise errors.NotEnoughCreditsError()

        elif 400 <= response.status_code < 500:
            raise errors.ClientError(reason)

        elif 501 == response.status_code:
            raise errors.UnsolvableRequestError()

        elif 500 <= response.status_code < 600:
            raise errors.ServerError(reason)
        else:
            raise errors.UnexpectedServerResponseError(f'{response.status_code} {reason}')
