#  Copyright (c) 2023-2025. OCX Consortium https://3docx.org. See the LICENSE

from pathlib import Path
import pytest
from ocx_common.utilities.downloader import SchemaDownloader
from tests.conftest import NAMESPACE

@pytest.mark.skip(reason="Remove this functionality")
def test_download_from_url(shared_datadir):
    """Test download from external source."""

    downloader = SchemaDownloader(shared_datadir)
    downloader.wget(NAMESPACE)
    files = list(shared_datadir.glob("*.xsd"))
    assert len(files) == 3


@pytest.mark.skip(reason="Remove this functionality")
def test_download_from_file(shared_datadir: Path):
    """Test download from a local file."""
    # Temp folder
    temp = shared_datadir / "temp"
    downloader = SchemaDownloader(temp)
    ocx_schema = shared_datadir / "schemas/OCX_Schema.xsd"
    downloader.wget(str(ocx_schema.resolve()))
    files = list(temp.glob("*.xsd"))
    assert len(files) == 3
