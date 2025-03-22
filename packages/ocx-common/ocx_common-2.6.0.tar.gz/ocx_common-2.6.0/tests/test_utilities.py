#  Copyright (c) 2024. OCX Consortium https://3docx.org. See the LICENSE

import os
from pathlib import Path

import pytest

# Project import
from ocx_common.utilities import utilities

from .conftest import MODEL_FOLDER, TEST_MODEL


def test_is_substring_in_list_1():
    assert utilities.is_substring_in_list(
        "Doe", ["John Doe", "Alicia", "Hello world", "package.file"]
    )


def test_is_substring_in_list_2():
    assert utilities.is_substring_in_list(
        ".file", ["John Doe", "Alicia", "Hello world", "package.file"]
    )


def test_is_substring_in_list_3():
    assert not utilities.is_substring_in_list(
        "Help", ["John Doe", "Alicia", "Hello world", "package.file"]
    )


def test_parent_directory(shared_datadir):
    file = shared_datadir / TEST_MODEL
    assert utilities.parent_directory(str(file.resolve())) == str(shared_datadir.resolve())


def test_all_equal_1():
    assert utilities.all_equal(["John", "John", "John", "John", "John", "John", "John"])


def test_all_equal_2():
    assert not utilities.all_equal(["John", "Alice", "John", "John", "John", "John", "John"])


def test_camel_case_split():
    assert utilities.camel_case_split("CamelCase") == ["Camel", "Case"]


def test_dromedary_case_split():
    assert utilities.dromedary_case_split("dromedaryCase") == ["dromedary", "Case"]


def test_list_files_in_directory(shared_datadir):
    folder = shared_datadir / MODEL_FOLDER
    assert utilities.list_files_in_directory(folder, "*.3docx") == [TEST_MODEL]


def test_resource_path(shared_datadir):
    file = Path.joinpath(shared_datadir, TEST_MODEL)
    path = utilities.resource_path(str(file))
    assert path == str(file)


def test_get_file_path(shared_datadir):
    file = Path.joinpath(shared_datadir, TEST_MODEL)
    path = utilities.get_file_path(str(file))
    assert path == str(file)

@pytest.mark.parametrize(
    "path, expected",
    [
        ("C:/Users/oca/AppData/Local/Temp/pytest-of-OCA/pytest-430/test_validate_10/data/models/NAPA-OCX_M1.3docx", True),  # ✅ Valid Windows absolute path
        ("C://Users/oca//NAPA-OCX_M1.3docx", True),  # ✅ Valid Windows absolute path with double slashes
        ("D://Users/oca//NAPA-OCX_M1.3docx", True),  # ✅ Valid Windows absolute path with double slashes
        ("../relative/path/file.txt", False), # ❌ ( relative path)
        ("C:Windows/System32/", False), # ❌  (Missing / after drive)
        ("K/Windows/System32/", False),  # ❌  (Missing : after drive)
    ],
)

def test_is_valid_absolute_windows_path(path, expected):
    assert utilities.is_valid_absolute_windows_path(path) == expected


@pytest.mark.parametrize(
    "path, expected",
    [
        ("/home/user/file.txt", True),  # ✅ Valid absolute path
        ("/var/log/system.log", True),  # ✅ Valid absolute
        ("./relative/path/to/file", True),  # ✅ Valid relative path
        ("../parent/directory/script.sh", True),  # ✅ Valid relative path
        ("~/Documents/file.pdf", True), # ✅ Valid home directory path
        ("/usr/local/bin/", True), # ✅Valid directory path
        (".hiddenfile", True), # ✅Valid hidden file
        ("/tmp/my_file-123.log", True), # ✅Valid tmp file
        ("home/user/file.txt", False),  # ❌ Missing leading `/`, `./`, or `../`
        ("/invalid|name/file.txt", False),  # ❌ Contains `|`
        ("/etc/passwd?query=1", False),  # ❌ Contains `?`
        ("C:\\Windows\\System32\\cmd.exe", False),  # ❌ Windows path
    ],
)

def test_valid_unix_paths(path, expected):
    assert(utilities.is_valid_unix_file_path(path)) == expected

@pytest.mark.parametrize(
    "uri, expected",
    [
        ("file://localhost:80/home/user/file.txt", False),  # ❌ remote file path
        ("file://server/path/to/file.txt", False),  # Added test case for remote file URI
        ("file://C:/user/system.log", True),  # ✅ Valid local absolute file path
        ("file://C://One Drive//path//to//file", True),  # ✅ Valid local relative path
        ("file://./parent/directory/script.sh", False),  # ✅ relative path
    ],
)

def test_is_local_file_uri(uri, expected):
    assert(utilities.is_local_file_uri(uri)) == expected


# #
# # @pytest.mark.parametrize(
# #     "path, expected",
# #     [
# #         ("C:/Users/oca/NAPA-OCX_M1.3docx", True) if os.name == 'nt' else ("home/user/file.txt", False),
# #         ("D:/Users/oca/NAPA-OCX_M1.3docx", True)if os.name == 'nt' else ("./relative/path/to/file", True),
# #         ("C:Windows/System32/", False) if os.name == 'nt' else ("/var/log/system.log", True),
# #     ],
# # )
#
# def test_is_valid_file_path(path, expected):
#     assert(utilities.is_valid_file_path(path)) == expected

def test_file_uri_to_path_1():
    assert utilities.file_uri_to_path("file:C:/User/john/myfile.txt") == "C:\\User\\john\\myfile.txt"

def test_file_uri_to_path_2():
    assert utilities.file_uri_to_path("file:///C:/User/john/myfile.txt") == "C:\\User\\john\\myfile.txt"

def test_file_uri_to_path_3():
    assert utilities.file_uri_to_path("file://server/share/myfile.txt") == "server\\share\\myfile.txt"

def test_file_uri_to_path_4():
    assert utilities.file_uri_to_path("file:///home/user/myfile.txt") == "\\home\\user\\myfile.txt"
