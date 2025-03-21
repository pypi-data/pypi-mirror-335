# -*- coding: utf-8 -*-

from pip_services4_components.refer import Descriptor, IReferences
from pip_services4_http.controller import RestOperations, RestController
from pip_services4_components.context import Context

from aichatconnect.modelmultiplexor.logic.IModelMultiplexorService import IModelMultiplexorService


class ModelMultiplexorOperations(RestOperations):
    def __init__(self):
        super().__init__()
        self._modelmultiplexor_service: IModelMultiplexorService = None
        self._dependency_resolver.put("modelmultiplexor-service", Descriptor('aichatconnect-modelmultiplexor', 'service', '*', '*', '1.0'))

    def configure(self, config):
        super().configure(config)

    def set_references(self, references: IReferences):
        super().set_references(references)
        self._modelmultiplexor_service = self._dependency_resolver.get_one_required('modelmultiplexor-service')

    def get_available_models(self):
        context = Context.from_trace_id(self._get_trace_id())
        filter_params = self._get_filter_params()
        paging_params = self._get_paging_params()
        try:
            res = self._modelmultiplexor_service.get_available_models(context, filter_params, paging_params)
            return self._send_result(res)
        except Exception as err:
            return self._send_error(err)

    def register_routes(self, controller: RestController):
        controller.register_route('get', '/available_models', None,
                                  self.get_available_models)
