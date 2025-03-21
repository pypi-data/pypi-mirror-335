# test_basic_client_v1_fixture.py
import pytest

from aichatconnect.anthropicmodelconnector.version1.IBasicClientV1 import IBasicClientV1
from aichatconnect.anthropicmodelconnector.version1.RequestV1 import RequestV1

class BasicClientV1Fixture:
    def __init__(self, client: IBasicClientV1):
        assert client is not None
        self._client = client

    def test_operations(self):
        """Test the basic operations"""

        # Happy path
        req = RequestV1(value="test_value")
        res = self._client.do_something(None, req)
        assert res is not None
        assert res.value == req.value

        # Boundary case
        req = RequestV1(value="")
        res = self._client.do_something(None, req)
        assert res.value == ""

        # Negative case
        with pytest.raises(Exception, match=r"NullPointerException"):
            self._client.do_something(None, None)
