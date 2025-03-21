# basic_mock_client_v1.py
from typing import Optional

from pip_services4_components.context import IContext

from .ResponseV1 import ResponseV1
from .RequestV1 import RequestV1
from .IBasicClientV1 import IBasicClientV1


class BasicMockClientV1(IBasicClientV1):
    def __init__(self):
        self._default_response = ""

    def do_something(self, context: Optional[IContext], request: RequestV1) -> ResponseV1:
        if request is None or not hasattr(request, "value"):
            raise ValueError("NullPointerException")

        response = ResponseV1(value=self._default_response)
        response.value = request.value if request.value else self._default_response
        return response
