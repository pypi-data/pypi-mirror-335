#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Module for server clients."""

# System imports
import json
from abc import ABC
from enum import Enum
from io import BytesIO
from typing import Dict

import pycurl
import requests

# Third party
from loguru import logger
from pycurl import error as pycurl_error
from requests.models import Response

# Project imports
from ocx_common.interfaces.interfaces import IRestClient


class RequestClientError(requests.RequestException):
    """Request client errors."""


class CurlClientError(pycurl_error):
    """Curl client errors."""


class EmbeddingMethod(Enum):
    """Embedding type."""

    STRING = "STRING"
    URL = "URL"
    BASE64 = "BASE64"


class RestClient(IRestClient, ABC):
    """
    Request client
    """

    def __init__(self, headers: Dict = None, timeout: int = 30):
        if headers is None:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        super().__init__(headers, timeout)
        self._session = requests.Session()

    def get(self, url: str, headers: dict = None) -> Response:
        """
            Get method.

        Args:
            headers: The request header dictionary
            url: The resource url

        Returns:
            The request Response object.

        Raises:
             RequestClientError on (HTTPError, ConnectionError).
        """

        try:
            if headers is None:
                headers = self._headers
            response = self._session.get(url, headers=headers, timeout=self._timeout)
            return response
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
        ) as err:
            logger.error(err)
            raise RequestClientError(err) from err

    def post(self, url: str, payload: Dict, headers: Dict = None) -> Response:
        """
            Post method.
        Args:
            headers: The request headers
            url: the resource.
            payload: The request body.

        Returns:
            The Response object.

        Raises:
              RequestClientError on (HTTPError, ConnectionError).
        """

        try:
            if headers is None:
                headers = self._headers
            response = self._session.post(
                url, headers=headers, json=payload, timeout=self._timeout
            )
            return response
        except (
            requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
        ) as err:
            logger.error(err)
            raise RequestClientError(err) from err

    def set_headers(self, headers: Dict):
        """
            Set the request headers
        Args:
            headers: The headers declaration

        """

        self._headers = headers

    def put(self, url: str, payload: Dict, headers: Dict = None) -> Response:
        """
            Put method.
        Args:
            headers: Request header
            url: the resource.
            payload: The request body.

        Returns:
            The Response object.

        Raises:
              RequestClientError on (HTTPError, ConnectionError).

        """

        raise RequestClientError("put method not implemented")

    def patch(self, url: str, payload: Dict, headers: Dict = None) -> Response:
        """
            Patch method.
        Args:
            headers: The request header
            url: the resource.
            payload: The request body.

        Returns:
            The Response object.

        Raises:
              RequestClientError on (HTTPError, ConnectionError).
        """

        raise RequestClientError("patch method not implemented")

    def delete(self, url: str, payload: Dict, headers: Dict = None) -> Response:
        """
            Delete method.
        Args:
            headers: The request header
            url: the resource.
            payload: The request body.

        Returns:
            The Response object.

        Raises:
              RequestClientError on (HTTPError, ConnectionError).
        """

        raise RequestClientError("delete method not implemented")


class CurlRestClient(IRestClient, ABC):
    """
    cURL client
    """

    def __init__(self, headers: Dict = None, timeout: int = 30):
        super().__init__(headers, timeout)

    def pycurl_to_requests_response(
        self, buffer: BytesIO, status_code: int
    ) -> Response:
        """A function to convert pycurl response to a requests Response object"""
        # Create a requests Response object
        response = Response()
        response._content = buffer.getvalue()  # Set the content of the response
        response.status_code = status_code  # Set the status code
        return response

    def get(self, url: str, headers: dict = None) -> Response:
        """
            Get method.

        Args:
            headers: Request header
            url: The resource endpoint

        Returns:
            The Response object.

        Raises:
             CurlClientError if the status code is not 200.
        """

        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.TIMEOUT, self._timeout)
        buffer = BytesIO()
        # Set the headers
        curl_headers = []
        if headers is None:
            for k in self._headers:
                curl_headers.append(f"{k}:{self._headers[k]}")
        curl.setopt(pycurl.HTTPHEADER, headers)
        # Set the write function to store the response in the buffer
        curl.setopt(pycurl.WRITEDATA, buffer)
        try:
            # Perform the request
            curl.perform()
            # Get the status code
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            # Get the response
            response = self.pycurl_to_requests_response(buffer, status_code)
            curl.close()
            return response
        except pycurl.error as e:
            msg = f"Failed to get data from {url}: Response: {e}"
            logger.error(msg)
            raise CurlClientError(msg) from e

    def post(self, url: str, payload: Dict, headers: Dict = None) -> Response:
        """
            Post method.
        Args:
            headers: The request headers
            url: the resource.
            payload: The request body.

        Returns:
            The Response object.

        Raises:
              RequestClientError on pycurl.error.
        """

        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        # curl.setopt(pycurl.TIMEOUT, self._timeout)
        body = json.dumps(payload)
        buffer = BytesIO()
        # Set the HTTP method to POST
        curl.setopt(pycurl.POST, 1)
        # Set the POST data
        curl.setopt(pycurl.POSTFIELDS, body)
        # Set the headers
        if headers is None:
            headers = self._headers
        curl.setopt(pycurl.HTTPHEADER, headers)
        # Create a BytesIO object to store the header data
        header_buffer = BytesIO()
        # Set the WRITEFUNCTION to write the header data to the BytesIO object
        curl.setopt(pycurl.HEADERFUNCTION, header_buffer.write)
        # Set the write function to store the response in the buffer
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        try:
            # Perform the request
            curl.perform()
            status_code = curl.getinfo(pycurl.HTTP_CODE)
            response = self.pycurl_to_requests_response(buffer, status_code)
            curl.close()
            return response
        except pycurl.error as e:
            msg = f"Failed to post data to {url}: Response: {e}"
            logger.error(msg)
            raise CurlClientError(msg) from e

    def set_headers(self, headers: Dict):
        """
        Set the request headers
        Args:
            headers: The headers declaration
        """
        self._headers = [f"{k}:{v}" for k, v in headers.items()]

    def put(self, url: str, payload: Dict, headers: Dict = None) -> Response:
        """
            Put method.
        Args:
            headers: Request header
            url: the resource.
            payload: The request body.

        Returns:
            The Response object.

        Raises:
              RequestClientError on (HTTPError, ConnectionError).

        """

        raise CurlClientError("put method not implemented")

    def patch(self, url: str, payload: Dict, headers: Dict = None) -> Response:
        """
            Patch method.
        Args:
            headers: The request header
            url: the resource.
            payload: The request body.

        Returns:
            The Response object.

        Raises:
              RequestClientError on (HTTPError, ConnectionError).
        """

        raise CurlClientError("patch method not implemented")

    def delete(self, url: str, payload: Dict, headers: Dict = None) -> Response:
        """
            Delete method.
        Args:
            headers: The request header
            url: the resource.
            payload: The request body.

        Returns:
            The Response object.

        Raises:
              RequestClientError on (HTTPError, ConnectionError).
        """

        raise CurlClientError("delete method not implemented")
