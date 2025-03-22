#  Copyright (c) 2025. #  OCX Consortium https://3docx.org. See the LICENSE


import json

# Project imports
from ocx_common.parser.parsers import OcxNotifyParser
from ocx_common.serializer.serializer import OcxSerializer
from tests.conftest import TEST_MODEL


def test_serialize_json(shared_datadir, data_regression):
    parser = OcxNotifyParser()
    model = shared_datadir / "models" / TEST_MODEL
    ocxxml = parser.parse(str(model.resolve()))
    serializer = OcxSerializer(ocxxml)
    result = serializer.serialize_json()
    data_regression.check(json.loads(result))


def test_serialize_xml(shared_datadir):
    parser = OcxNotifyParser()
    model = shared_datadir / "models"/ TEST_MODEL
    ocxxml = parser.parse(str(model.resolve()))
    serializer = OcxSerializer(ocxxml)
    result = serializer.serialize_xml()
    assert '?xml version' in result
