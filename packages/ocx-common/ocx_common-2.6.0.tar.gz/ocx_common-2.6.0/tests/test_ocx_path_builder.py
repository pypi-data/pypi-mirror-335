#  Copyright (c) 2024. #  OCX Consortium https://3docx.org. See the LICENSE

# Third party imports
from lxml import etree

from ocx_common.parser.parsers import OcxModelParser
from ocx_common.utilities.ocx_xml import OcxXml
from ocx_common.x_path.x_path import OcxPathBuilder
from ocx_common.x_path.xelement import LxmlElement

# Project imports
from .conftest import MODEL_FOLDER, NAMESPACE, SCHEMA_VERSION, TEST_MODEL


class TestXPathBuilder:
    def test_select_all_named_nodes(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser =OcxModelParser(str(file))
        root = parser.get_root()
        search = etree.XPath(
            path=OcxPathBuilder.select_all_named_nodes("RefPlane", namespace="ocx"),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(root)
        assert len(result) == 13

    def test_select_all_named_unitsml_nodes(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        print(root.nsmap)
        search = etree.XPath(
            path=OcxPathBuilder.select_all_named_nodes("Unit", namespace="unitsml"),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(root)
        assert len(result) == 17

    def test_select_current_node_is_root(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        search = etree.XPath(
            path=OcxPathBuilder.select_current_node(),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(root)
        node = result[0]
        assert (
            node.get("schemaVersion") == SCHEMA_VERSION
            and node.tag == f"{LxmlElement.namespaces_decorate(NAMESPACE)}ocxXML"
        )

    def test_select_current_node_is_vessel(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        vessel = LxmlElement.find_child_with_name(element=root, child_name="Vessel")
        search = etree.XPath(
            path=OcxPathBuilder.select_current_node(),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(vessel)
        node = result[0]
        assert (
            node.get("name") == "OCX-MODEL1/A"
            and node.tag == f"{LxmlElement.namespaces_decorate(NAMESPACE)}Vessel"
        )

    def test_select_parent_node_is_vessel(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        panel = LxmlElement.find_child_with_name(root, "Panel")
        search = etree.XPath(
            path=OcxPathBuilder.select_parent_node(),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(panel)
        parent = result[0]
        assert (
            parent.get("id") == "nplcid1"
            and parent.tag == f"{LxmlElement.namespaces_decorate(NAMESPACE)}Vessel"
        )

    def test_select_named_parent_node_is_coordinate_system(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        x_ref = LxmlElement.find_child_with_name(root, "XRefPlanes")
        search = etree.XPath(
            path=OcxPathBuilder.select_named_parent_node(parent="CoordinateSystem"),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(x_ref)
        parent = result[0]
        assert (
            parent.get("id") == "nplcid7"
            and parent.tag
            == f"{LxmlElement.namespaces_decorate(NAMESPACE)}CoordinateSystem"
        )

    def test_select_named_node_xrefplanes(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        search = etree.XPath(
            path=OcxPathBuilder.select_named_nodes("XRefPlanes"),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(root)
        assert len(result) == 1

    def test_select_all_nodes_with_attribute_name_guidref(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        search = etree.XPath(
            path=OcxPathBuilder.select_any_nodes_with_global_attribute_name("GUIDRef"),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(root)
        assert len(result) == 35

    def test_select_named_nodes_with_attribute_name_panel(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        search = etree.XPath(
            path=OcxPathBuilder.select_named_nodes_with_global_attribute_name(
                node_name="Panel", attribute_name="GUIDRef"
            ),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(root)
        assert (
            len(result) == 1
            and result[0].tag == f"{LxmlElement.namespaces_decorate(NAMESPACE)}Panel"
        )

    def select_named_nodes_with_attribute_value_of_guidref(self, shared_datadir):
        guidref = "6e17c799-8e76-416d-ba75-ca0565dd3c42"
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        search = etree.XPath(
            path=OcxPathBuilder.select_named_nodes_with_global_attribute_value(
                node_name="Panel", attribute_name="GUIDRef", attribute_value=guidref
            ),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(root)
        assert len(result) == 1 and result[0].get("GUIDRef") == guidref

    def select_any_nodes_with_attribute_value(self, shared_datadir):
        guidref = "6e17c799-8e76-416d-ba75-ca0565dd3c42"
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        search = etree.XPath(
            path=OcxPathBuilder.select_any_nodes_with_attribute_value(
                attribute_name="GUIDRef", attribute_value=guidref
            ),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(root)
        assert len(result) == 1 and result[0].get("GUIDRef") == guidref

    def test_select_all_nodes_with_attribute_name(self, shared_datadir):
        file = shared_datadir / MODEL_FOLDER / TEST_MODEL
        parser = OcxModelParser(str(file))
        root = parser.get_root()
        search = etree.XPath(
            path=OcxPathBuilder.select_named_nodes_with_local_attribute_name(
                node_name="EnumeratedRootUnit",
                attribute_name="prefix",
                namespace="unitsml",
            ),
            namespaces=OcxXml.get_all_namespaces(str(file)),
        )
        result = search(root)

        assert len(result) == 9
