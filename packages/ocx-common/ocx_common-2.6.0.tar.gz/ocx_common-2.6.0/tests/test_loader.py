#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

from ocx_common.loader.loader import DeclarationOfOcxImport, DynamicLoader
from ocx_common.parser.parsers import MetaData
from tests.conftest import SCHEMA_VERSION


def test_import_ocx_286():
    declaration = DeclarationOfOcxImport("ocx", "2.8.6")
    assert DynamicLoader.import_module(declaration)

def test_import_ocx_300():
    declaration = DeclarationOfOcxImport("ocx", "3.0.0")
    assert DynamicLoader.import_module(declaration)

def test_import_class():
    declaration = DeclarationOfOcxImport("ocx", SCHEMA_VERSION)
    assert DynamicLoader.import_class(declaration, "Vessel")


def test_ref_type_name():
    class_name = "RefTypeValue"
    value = "OCX_VESSEL"
    declaration = DeclarationOfOcxImport("ocx", SCHEMA_VERSION)
    data_class = DynamicLoader.import_class(declaration, class_name)
    instance = getattr(data_class, value)
    assert instance.name == "OCX_VESSEL"


def test_data_class_instance_namespace():
    class_name = "Vessel"
    declaration = DeclarationOfOcxImport("ocx", SCHEMA_VERSION)
    data_class = DynamicLoader.import_class(declaration, class_name)()
    namespace = MetaData.namespace(data_class)
    repo_folder = SCHEMA_VERSION.replace(".", "")
    repo_folder = f"V{repo_folder}"
    assert (
        namespace
        == f"https://3docx.org/fileadmin//ocx_schema//{repo_folder}//OCX_Schema.xsd"
    )


def test_get_all_class_names():
    classes = DynamicLoader.get_all_class_names("ocx", "3.0.0")
    assert len(classes) == 504


def test_get_declaration():
    declaration = DeclarationOfOcxImport("ocx", SCHEMA_VERSION).get_declaration()
    assert declaration == "ocx.ocx_300.ocx_300"


def test_get_name():
    name = DeclarationOfOcxImport("ocx", SCHEMA_VERSION).get_name()
    assert name == "ocx"


def test_get_version():
    version = DeclarationOfOcxImport("ocx", SCHEMA_VERSION).get_version()
    assert version == SCHEMA_VERSION
