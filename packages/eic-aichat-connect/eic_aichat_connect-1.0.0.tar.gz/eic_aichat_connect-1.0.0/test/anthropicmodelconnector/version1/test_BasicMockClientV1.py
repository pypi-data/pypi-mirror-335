# test_basic_mock_client_v1.py
import pytest

from aichatconnect.anthropicmodelconnector.version1.BasicMockClientV1 import BasicMockClientV1
from test.anthropicmodelconnector.version1.BasicClientV1Fixture import BasicClientV1Fixture


@pytest.fixture(scope="module")
def client():
    return BasicMockClientV1()


def test_crud_operations(client):
    fixture = BasicClientV1Fixture(client)
    fixture.test_operations()
