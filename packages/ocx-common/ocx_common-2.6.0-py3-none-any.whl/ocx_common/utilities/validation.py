#  Copyright (c) 2025. #  OCX Consortium https://3docx.org. See the LICENSE


import os
import urllib.parse
from pathlib import Path

import requests

# Third party imports
from loguru import logger

from ocx_common.decorators.decorators import exception_handler

# Project imports
from ocx_common.utilities.utilities import (
    is_local_file_uri,
    is_valid_absolute_windows_path,
    is_valid_unix_file_path,
    is_windows_drive_letter,
)


class URIError(BaseException):
    """URIValidator errors."""


class URIValidator:
    """
    URI and OS source validation.
    Check both correctness and existence of the source.
    """

    def __init__(self, uri: str):
        self.uri = uri

    @exception_handler(BaseException)
    def is_valid(self, check_source: bool = False) -> bool:
        """Validates whether the input is a correct URI or a valid file path.

        Args:
            check_source: If True, check if the source of the URI exists.
        Raises:
            URIError if the source does not exist and check_source is True
        """
        # The uri is an OS file path
        if self._validate_local_file(check_source):
            return True
        try:
            parsed = urllib.parse.urlparse(self.uri)
            if parsed.scheme in ("http", "https"):
                return self._validate_http_uri(parsed, check_source)
            elif parsed.scheme == "file":
                return self._validate_file_scheme(parsed)
            else:
                e = f"Existence of the scheme {parsed.scheme} is not supported"
                logger.error(e)
                if check_source:
                    raise URIError(e)
                return self._is_valid_uri(parsed)
        except (ValueError, URIError) as e:
            logger.error(e)
            raise URIError from e

    def _is_valid_file_path(self, file_path: str) -> bool:
        """Checks if the given path is a valid file path."""
        # on Windows
        if os.name == "nt":
            return is_valid_absolute_windows_path(file_path)
        # On UNIX like os
        else:
            return is_valid_unix_file_path(file_path)

    def _is_valid_uri(self, parsed) -> bool:
        """Validates whether the given URI has a correct structure."""
        return bool(parsed.scheme and parsed.netloc)

    def _file_exists(self, path: str) -> bool:
        path_to_file = Path(path)
        return path_to_file.exists()

    def _uri_exists(self, check_source: bool) -> bool:
        if not check_source:
            return True
        response = requests.head(self.uri)
        if response.status_code == 200:
            logger.info(f"The {self.uri} is accessible")
            return True
        elif response.status_code == 404:
            msg = f"The URI {self.uri} does not exist. Server response: {response.text}"
            logger.error(msg)
            raise URIError(msg)
        else:
            e = f"(The request returned {response.text}"
            raise URIError(e)

    def is_local_file(self) -> bool:
        if is_valid_absolute_windows_path(self.uri):
            return True
        parsed = urllib.parse.urlparse(self.uri)
        if parsed.scheme == "file":
            if is_windows_drive_letter(parsed.netloc):
                return True
            else:
                return False
        elif parsed.scheme == "":
            return is_valid_absolute_windows_path(self.uri)
        else:
            return False

    def _validate_local_file(self, check_source: bool) -> bool:
        if self._is_valid_file_path(self.uri):
            return self._file_exists(self.uri) if check_source else True
        return False

    def _validate_http_uri(self, parsed, check_source: bool) -> bool:
        if not self._is_valid_uri(parsed):
            return False
        return self._uri_exists(check_source)

    def _validate_file_scheme(self, parsed) -> bool:
        if parsed.path == "":
            logger.error(f"Missing valid absolute path in {self.uri}")
            return False
        if is_local_file_uri(self.uri):
            return is_valid_absolute_windows_path(
                parsed.path
            ) and self._is_valid_file_path(parsed.path)
        return False
