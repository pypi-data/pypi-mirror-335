#  Copyright (c) 2023-2025. OCX Consortium https://3docx.org. See the LICENSE
import re
from pathlib import Path
from typing import Optional

from loguru import logger
from xsdata.codegen import opener

# Third part imports
from xsdata.utils.downloader import Downloader

from ocx_common.decorators.decorators import exception_handler

# Module imports
from ocx_common.utilities.validation import URIValidator


def set_schema_location_to_local_file(xsd_content: str) -> str:
    pattern = r'schemaLocation="([^"]+)"'  # Capture the value inside schemaLocation=""
    match = re.search(pattern, xsd_content)  # Find the first occurrence
    if match:
        schema_location = match.group(1)  # Return the extracted schemaLocation value
        schema_file = Path(schema_location).name
        # Replace it with the new local location
        new_location = f"file://.{schema_file}"
        updated_xsd = re.sub(
            pattern, f'schemaLocation="{new_location}"', xsd_content, count=1
        )
        return updated_xsd
    else:
        logger.debug("No schema location found")
        return xsd_content


class SchemaDownloader(Downloader):
    """Downloader specialisation class.

    Arguments:
        output: The location of the download folder relative to current directory

    Args:
        folder: The download target folder.

    Properties:
        schema_folder: The path to the schema download folder
        change_schema_location: Replace the ``schemaLocation`` attribute with the new schema location.
    """

    def __init__(self, folder: Path, change_schema_location: bool = True):
        super().__init__(folder)
        self.schema_folder = folder
        self.change_schema_location = change_schema_location

    def write_file(self, uri: str, location: Optional[str], content: str):
        """
        Override super class method and output all schemas into one folder.

        Arguments:
            content: The schema content.
            location: The download location.
            uri: the download target resource. All referenced schemas will be collected.
        """
        # Get the uri file name
        name = Path(uri).name
        file_path = self.schema_folder / name
        file_path.write_text(content, encoding="utf-8")
        logger.debug(
            f"Writing schema {file_path.resolve()} to folder {self.schema_folder.resolve()}"
        )
        # logger.debug(content)
        self.downloaded[uri] = file_path

        if location:
            self.downloaded[location] = file_path

    @exception_handler(BaseException)
    def wget(self, uri: str, location: Optional[str] = None):
        """Download handler for any uri input with circular protection.
        Override super class method to handle a local file.

        """
        validator = URIValidator(uri)
        if validator.is_valid():
            if not (
                uri in self.downloaded or (location and location in self.downloaded)
            ):
                self.downloaded[uri] = None
                self.downloaded[location] = None
                self.adjust_base_path(uri)

                logger.info(f"Fetching {uri}")
                if validator.is_local_file():
                    with open(uri, "rb") as file:
                        input_stream = file.read()
                else:
                    input_stream = opener.open(uri).read()  # nosec
        else:
            input_file = Path(uri).resolve()
            with open(str(input_file), "rb") as file:
                input_stream = file.read()
        if uri.endswith("wsdl"):
            self.parse_definitions(uri, input_stream)
        else:
            self.parse_schema(uri, input_stream)
            # replace the schema location
            content = input_stream.decode()
            if self.change_schema_location:
                content = set_schema_location_to_local_file(content)
            self.write_file(uri, location, content)
