# basic_rest_client_v1.py
from pip_services4_http.clients import RestClient
from pip_services4_components.config import ConfigParams
from pip_services4_components.context import IContext

from .ResponseV1 import ResponseV1
from .RequestV1 import RequestV1
from .IBasicClientV1 import IBasicClientV1


class BasicRestClientV1(RestClient, IBasicClientV1):
    def __init__(self, config: ConfigParams = None):
        """
        Initializes a new instance of the BasicRestClientV1.

        :param config: Configuration parameters.
        """
        super().__init__()
        self._base_route = "basic/v1"

        if config is not None:
            self.configure(config)

    def do_something(self, context: IContext, request: RequestV1) -> ResponseV1:
        """
        Calls the remote service to perform an operation.

        :param context: Context for tracing execution.
        :param request: The request object containing the value.
        :return: The response object.
        """
        if request is not None:
            timing = self._instrument(context, self._base_route + ".do_something")

            try:
                res = self._call(
                    'post',
                    '/do_something',
                    context,
                    None,
                    request
                )
                timing.end_timing()
                return ResponseV1(value=res.get("value")) if res else None
            except Exception as err:
                timing.end_failure(err)
                raise err
        else:
            raise ValueError("NullPointerException")
