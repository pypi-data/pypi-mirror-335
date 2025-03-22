#  Copyright (c) 2025. #  OCX Consortium https://3docx.org. See the LICENSE
"""Mock server for client requests."""

import pytest
import responses

from tests.conftest import MOCK_URL


@pytest.fixture
def mock_server():
    """Mock server for HTTP requests."""
    endpoints = [
        {
            "method": responses.GET,
            "url": f"{MOCK_URL}/get_200",
            "json": {"id": 1, "name": "John Doe"},
            "status": 200,
        },
        {
            "method": responses.POST,
            "url": f"{MOCK_URL}/post_201",
            "json": {"id": 1, "name": "John Doe"},
            "status": 201,
        },
        {
            "method": responses.GET,
            "url": f"{MOCK_URL}/get_400",
            "json": {"error": "Bad Request"},
            "status": 400,
        },
    ]

    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        for endpoint in endpoints:
            rsps.add(
                method=endpoint["method"],
                url=endpoint["url"],
                json=endpoint["json"],
                status=endpoint["status"],
            )
        yield rsps
