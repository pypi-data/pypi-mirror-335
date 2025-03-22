#  Copyright (c) 2023-2024. #  OCX Consortium https://3docx.org. See the LICENSE
"""Shared utility classes and functions"""

# System imports
import errno
import os
import re
import sys
import urllib.parse
from collections import defaultdict
from itertools import groupby
from pathlib import Path
from typing import Any, Dict, Generator, List

# Third party imports
# Project imports


def is_substring_in_list(substring, string_list):
    """

    Args:
        substring: The search string
        string_list: List of strings

    Returns:
        True if the substring is found, False otherwise.
    """
    return any(substring in string for string in string_list)


def all_equal(iterable) -> bool:
    """
    Verify that all items in a list are equal
    Args:
        iterable:

    Returns:
        True if all are equal, False otherwise.
    """
    g = groupby(iterable)
    return next(g, True) and not next(g, False)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath(".."))
    return os.path.join(base_path, relative_path)


def parent_directory(file: str) -> str:
    """The full path to the folder containing the ``file``

    Args:
        file: The name of an existing file
    """
    return os.path.realpath(os.path.join(os.path.dirname(file), ""))


def nested_dict():
    """
    A recursive function that creates a default dictionary where each value is
    another default dictionary.
    """
    return defaultdict(nested_dict)


def get_key_from_value(my_dict, value) -> Any:
    """
        Return the key associated with the value
    Args:
        my_dict: The dictionary of key, value pairs
        value: The value to search for

    Returns:
        The key if found
    Raises:
        ValueError if the value does not exist in the dictionary.
    """
    for key, val in my_dict.items():
        if val == value:
            return key
    raise ValueError(
        f"The value {value} does not exist in the dictionary"
    )  # raise a ValueError if the value is not found


def default_to_regular(d) -> Dict:
    """
    Converts defaultdict of defaultdict to dict of dicts.

    Args:
        d: The dict to be converted

    """
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d


def default_to_grid(d) -> Dict:
    """
    Converts defaultdicts to a data grid with unique row ids.

    Args:
        d: The dict to be converted

    """
    if isinstance(d, defaultdict):
        print(d.items())
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d


def list_files_in_directory(directory: str, filter: str) -> List:
    """
    Lists files in a directory based on a specified filter using glob pattern matching.

    Args:
        directory (str): The path to the directory.
        filter (str): The filter pattern to apply when listing files.

    Returns:
        List: A list of file paths that match the filter criteria.
    Raises:
        AssertionError: If the directory does not exist.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise AssertionError(errno.EEXIST)
    return [file.name for file in dir_path.glob(filter) if file.is_file()]


def camel_case_split(str) -> List:
    """Split camel case string to individual strings."""
    return re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", str)


def dromedary_case_split(str) -> List:
    """Split camel case string to individual strings."""
    return re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", str)


def get_file_path(file_name):
    """Get the correct file path also when called within a one-file executable."""
    base_path = sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.abspath("..")
    return os.path.join(base_path, file_name)


def is_valid_absolute_windows_path(path: str) -> bool:
    """
    Returns True if the path is a valid absolute Windows path.

    Args:
        path (str): The path to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    if not path:
        return False

    # Normalize slashes (convert forward slashes to backslashes)
    path = path.replace("/", "\\")

    # Windows MAX_PATH limit (excluding long path support)
    if len(path) > 260:
        return False

    # Ensure the path starts with a valid drive letter or UNC path
    drive_letter_pattern = re.compile(r"^[a-zA-Z]:\\")
    unc_pattern = re.compile(r"^\\\\[^\\/:*?\"<>|\r\n]+\\[^\\/:*?\"<>|\r\n]+")

    if not (drive_letter_pattern.match(path) or unc_pattern.match(path)):
        return False

    # Ensure `os.path.isabs()` confirms it as an absolute path
    if not os.path.isabs(path):
        return False

    return True


def is_windows_drive_letter(scheme: str) -> bool:
    """

    Args:
        scheme: The urlparse scheme

    Returns:
        True if the scheme is a valid Windows drive letter
    """
    return bool(re.fullmatch(r"[A-Za-z]:", scheme))


def is_valid_unix_file_path(path: str) -> bool:
    """
        Return True if the path is a valid UNIX path
    Args:
        path: path to validate

    Returns: True if validated, False otherwise.

    """
    unix_pattern = re.compile(
        r"^(\/|\.{1,2}\/|~\/|\.)(?:[a-zA-Z0-9._-]+\/)*[a-zA-Z0-9._-]+\/?$"
    )
    return bool(unix_pattern.fullmatch(path))


def is_valid_file_path(path: str) -> bool:
    """

    Args:
        path:

    Returns:

    """
    if os.name == "nt":
        return is_valid_absolute_windows_path(path)
    else:
        return is_valid_unix_file_path(path)


def is_local_file_uri(uri: str) -> bool:
    """Return True if the file uri is a local file"""
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme == "file" and is_windows_drive_letter(parsed.netloc):
        file_path = f"{parsed.netloc}{parsed.path}"
        return is_valid_file_path(file_path)
    else:
        return False


def file_uri_to_path(uri: str) -> str:
    """Converts a file:// URI to a proper file system path."""
    if "file" in uri:
        parsed = urllib.parse.urlparse(uri)

        # Handle Windows UNC paths (file://server/share/file.txt → \\server\share\file.txt)
        if parsed.netloc:
            file_path = f"{parsed.netloc}{parsed.path}"
        else:
            file_path = parsed.path

        # Strip leading slash for Windows drive letters (e.g., /C:/path → C:/path)
        if (
            os.name == "nt"
            and file_path.startswith("/")
            and len(file_path) > 2
            and file_path[2] == ":"
        ):
            file_path = file_path[1:]

        # Normalize for the OS (Windows backslashes, Unix forward slashes)
        return os.path.normpath(file_path)
    else:
        raise ValueError(f"{uri} is not a valid file uri")


def iter_files(directory: str, filter_str: str) -> Generator:
    """
    Iterate over files in a directory based on a specified filter pattern.

    Args:
        directory (str): The path to the directory.
        filter_str (str): The filter pattern to apply when filtering files.

    Returns:
        Generator: A generator yielding file paths that match the filter criteria.

    """
    folder_path = Path(directory)
    if folder_path.is_dir():
        # Using glob to filter files based on a pattern
        for file_path in folder_path.glob(filter_str):
            yield file_path
