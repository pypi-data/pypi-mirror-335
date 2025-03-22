#  Copyright (c) 2025. #  OCX Consortium https://3docx.org. See the LICENSE
from ocx_common.utilities.ocx_xml import OcxXml
from tests.conftest import MODEL_FOLDER, NAMESPACE, SCHEMA_VERSION, TEST_MODEL


class TestOcxXml:
    def test_get_version(self, shared_datadir):
        model = shared_datadir / MODEL_FOLDER / TEST_MODEL
        assert OcxXml.get_version(str(model.resolve())) == SCHEMA_VERSION

    def test_get_ocx_namespace(self, shared_datadir):
        model = shared_datadir / MODEL_FOLDER / TEST_MODEL
        assert OcxXml.get_ocx_namespace(str(model.resolve())) == NAMESPACE

    def test_get_all_namespaces(self, shared_datadir, data_regression):
        model = shared_datadir / MODEL_FOLDER / TEST_MODEL
        result = OcxXml.get_all_namespaces(str(model.resolve()))
        data_regression.check(result)

    def test_has_ocx_namespace(self, shared_datadir):
        model = shared_datadir / MODEL_FOLDER / TEST_MODEL
        assert OcxXml.has_ocx_namespace(str(model.resolve())) == True

    def test_has_unitsml_namespace(self, shared_datadir):
        model = shared_datadir / MODEL_FOLDER / TEST_MODEL
        assert OcxXml.has_unitsml_namespace(str(model.resolve())) == True
