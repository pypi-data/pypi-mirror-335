#  Copyright (c) 2024. #  OCX Consortium https://3docx.org. See the LICENSE
from pathlib import Path
# Project imports
from ocx_common.parser.parsers import OcxNotifyParser, OcxModelParser, XsdParser

from .conftest import MODEL_FOLDER, TEST_MODEL, NAMESPACE


class TestNotifyParser:
    def test_parse(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxNotifyParser()
        root = parser.parse(str(file))
        name = root.header.name
        assert name == "OCX-MODEL1/A"


class TestOcxParser:
    def test_parse(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        assert (
            root.tag
            == "{https://3docx.org/fileadmin//ocx_schema//V300//OCX_Schema.xsd}ocxXML"
        )


class TestXSDParser:
    def test_parse(self, shared_datadir):
        schema_path = shared_datadir / "schemas" / "OCX_Schema.xsd"
        schema_parser = XsdParser(target_namespace="https://3docx.org/fileadmin//ocx_schema//V300//OCX_Schema.xsd",
                                  location="https://3docx.org/fileadmin//ocx_schema//V300//OCX_Schema.xsd")
        schema_content = schema_path.read_text()
        schema = schema_parser.parse_from_string(schema_content)
        assert schema.location == "https://3docx.org/fileadmin//ocx_schema//V300//OCX_Schema.xsd"

# def test_parser_invalid_source(shared_datadir):   # ToDO: Add edge test case when source does not exist
#     file = shared_datadir / "not_exist.3docx"
#     try:
#         OcxModelParser(str(file))
#         assert False
#     except OcxParserError:
#         assert True
