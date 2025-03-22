# ibasic_client_v1.py
from abc import ABC, abstractmethod
from typing import Optional

from pip_services4_components.context import IContext

from .ResponseV1 import ResponseV1
from .RequestV1 import RequestV1

class IBasicClientV1(ABC):
    @abstractmethod
    def do_something(self, context: Optional[IContext], request: RequestV1) -> ResponseV1:
        pass
