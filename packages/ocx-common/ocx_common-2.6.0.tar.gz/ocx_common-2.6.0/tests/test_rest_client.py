#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

import pytest

from ocx_common.clients.clients import RestClient
from tests.conftest import MOCK_URL
from tests.mock_rest_responses import mock_server

client = RestClient()


class TestRestClient:
    @pytest.mark.commit(reason="Implement mock server")

    def test_rest_get_200(self, mock_server):
        url = f'{MOCK_URL}/get_200'
        response = client.get(url=url)
        user_data = response.json()
        assert response.status_code == 200
        assert user_data['id'] == 1
        assert user_data['name'] == 'John Doe'

    @pytest.mark.commit(reason="Implement mock server")
    def test_rest_get_400(self, mock_server):
        url = f'{MOCK_URL}/get_400'
        response = client.get(url=url)
        assert response.status_code == 400
        assert response.json()['error'] == 'Bad Request'

    @pytest.mark.commit(reason="Implement mock server")
    def test_post_201(self, mock_server):
        url = f'{MOCK_URL}/post_201'
        payload = {'id': 1,
                   'name': 'John Doe'}
        response = client.post(url=url, payload=payload)
        user_data = response.json()
        # Assertions to verify the response handling
        assert response.status_code == 201
        assert user_data['id'] == 1
        assert user_data['name'] == 'John Doe'
