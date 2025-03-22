#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""OcxSerializer module."""

# system imports
from dataclasses import dataclass
from enum import Enum


# 3rd party imports
from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.serializers import JsonSerializer, XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig


# Project imports
from ocx_common.parser.parsers import MetaData


class ReportFormat(Enum):
    """Serialisation formats"""

    CSV = "csv"
    PARQUET = "parquet"


class OcxSerializer:
    """OcxSerializer class for 3Docx XML models."""

    def __init__(
        self,
        ocx_model: dataclass,
        pretty_print: bool = True,
        pretty_print_indent: str = "  ",
        encoding: str = "utf-8",
    ):
        """
        Args:
            ocx_model: The dataclass to serialize.
            pretty_print: True to pretty print, False otherwise.
            pretty_print_indent: Pretty print indentation.
            encoding: The encoding code.
        Params:
            _model: The dataclass to serialize.
            _config: The serializer configuration.

        """
        self._model: dataclass = ocx_model
        self._config = SerializerConfig(
            encoding=encoding,
            xml_version="1.0",
            xml_declaration=True,
            pretty_print=True,
            ignore_default_attributes=False,
            schema_location=None,
            no_namespace_schema_location=None,
            globalns=None,
        )

    def serialize_xml(self, global_ns: str = "ocx") -> str:
        """Serialize a 3Docx XML file with proper indentations.

        Returns:
              The dataclass xml serialisation.

        Raises:
            SerializeError if failing
        """
        target_ns = MetaData.namespace(self._model)
        ns_map = {global_ns: target_ns}
        serializer = XmlSerializer(context=XmlContext(), config=self._config)
        return serializer.render(self._model, ns_map=ns_map)

    def serialize_json(self) -> str:
        """Serialize a 3Docx XML model to json with proper indentations.

        Returns:
              The dataclass xml serialisation.

        Raises:
            SerializeError if failing
        """
        serializer = JsonSerializer(context=XmlContext(), config=self._config)
        return serializer.render(self._model)


# class Serializer:
#     """A general serializer for dict type data structures"""
#
#     @staticmethod
#     def serialize_to_csv(table: List, file_name: str):
#         """
#         Serialize a list of dictionaries to a csv file. Each dictionary is a row with ``key:value`` pairs
#         where the key is the column header and the value is the data value.
#         Args:
#             table: The table to serialize
#             file_name: the output file name
#         """
#         with open(file_name, 'w', newline='') as csvfile:
#             fieldnames = table[0].keys()
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writeheader()
#             writer.writerows(table)
#
#     @staticmethod
#     def serialize_to_parquet(report: ReportDataFrame, report_folder: str):
#         """
#         Serialize a dataframe report to a parquet file
#         Args:
#             report: Dataclass containing the dataframe to serialize
#             report_folder: the output directory
#         """
#         try:
#             stem = Path(report.source).stem
#             ocx_type = report.type.value.lower()
#             file_name = Path(report_folder).joinpath(f'{stem}_{ocx_type}.parquet')
#             df = report.elements
#             df.to_parquet(file_name)
#         except (pyarrow.lib.ArrowException, pyarrow.lib.ArrowInvalid) as e:
#             logger.error(f'Error serializing to parquet: {e}')
#             raise SerializerError(e) from e
#


class SerializerError(ValueError):
    """OCX Serializing errors."""
