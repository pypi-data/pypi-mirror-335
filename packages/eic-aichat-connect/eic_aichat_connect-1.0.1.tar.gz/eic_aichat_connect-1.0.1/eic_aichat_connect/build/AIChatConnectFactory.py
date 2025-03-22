# -*- coding: utf-8 -*-
from pip_services4_components.refer import Descriptor
from pip_services4_components.build import Factory

from eic_aichat_connect.modelmultiplexor.logic.ModelMultiplexorService import ModelMultiplexorService
from eic_aichat_connect.anthropicmodelconnector.version1.BasicMockClientV1 import BasicMockClientV1
from eic_aichat_connect.anthropicmodelconnector.version1.BasicRestClientV1 import BasicRestClientV1


class AIChatConnectFactory(Factory):
    __ServiceDescriptor = Descriptor('aichatconnect-modelmultiplexors', 'service', 'default', '*', '1.0')

    __MockAnthropicmodelconnectorClientDescriptor = Descriptor("aichatconnect-anthropicmodelconnector", "client", "mock", "*", "1.0")
    __HttpAnthropicmodelconnectorClientDescriptor = Descriptor("aichatconnect-anthropicmodelconnector", "client", "http", "*", "1.0")


    def __init__(self):
        super().__init__()

        self.register_as_type(self.__ServiceDescriptor, ModelMultiplexorService)

        self.register_as_type(self.__MockAnthropicmodelconnectorClientDescriptor, BasicMockClientV1)
        self.register_as_type(self.__HttpAnthropicmodelconnectorClientDescriptor, BasicRestClientV1)
