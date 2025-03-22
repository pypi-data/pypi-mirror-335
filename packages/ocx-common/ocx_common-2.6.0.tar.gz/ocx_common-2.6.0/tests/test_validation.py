#  Copyright (c) 2025. #  OCX Consortium https://3docx.org. See the LICENSE
from pathlib import Path

import pytest

from ocx_common.utilities.validation import URIValidator
from tests.conftest import MODEL_FOLDER, TEST_MODEL


def test_validate_and_existence(shared_datadir):
    uri = shared_datadir / MODEL_FOLDER / TEST_MODEL
    validator = URIValidator(str(uri.resolve()))
    assert validator.is_valid(check_source=True)

@pytest.mark.parametrize(
    "uri, expected",
    [
        ("C:/Users/oca/AppData/Local/Temp/pytest-of-OCA/pytest-430/test_validate_10/data/models/NAPA-OCX_M1.3docx", True),  # ✅ Valid Windows absolute path
        ("https://3docx.org/fileadmin//ocx_schema//V300//OCX_Schema.xsd", True),  # ✅ A valid uri
        ("file://.path.txt", False),  # ❌  Windows local path
        ("https:3docx.org/fileadmin//ocx_schema//V300//OCX_Schema.xsd", False),  # ❌ Missing slashes
        ("file://C|/invalid/path.txt", False),  # ❌ Incorrect Windows drive format
        ("file:\\backslashes\\wrong.txt", False),  # ❌ Backslashes are not allowed
    ],
)
def test_validate(uri, expected):
    validator = URIValidator(uri)
    assert validator.is_valid() == expected

@pytest.mark.parametrize(
    "uri, expected",
    [
        ("C:/Users/oca/AppData/Local/Temp/pytest-of-OCA/pytest-430/test_validate_10/data/models/NAPA-OCX_M1.3docx", True),  # ✅ Valid Windows absolute path
        ("file://.path.txt", False),  # ❌  Local, but not absolute path
        ("https:3docx.org/fileadmin//ocx_schema//V300//OCX_Schema.xsd", False),  # ❌ Remote
        ("file://C:/users/path.txt", True),  # ✅  Local
    ],
)
def test_is_local_file(uri, expected):
    validator = URIValidator(uri)
    assert validator.is_local_file() == expected
