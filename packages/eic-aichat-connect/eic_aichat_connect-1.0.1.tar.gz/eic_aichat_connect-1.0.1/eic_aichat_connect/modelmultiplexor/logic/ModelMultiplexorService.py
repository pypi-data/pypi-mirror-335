# -*- coding: utf-8 -*-
from typing import Optional

from pip_services4_components.config import ConfigParams, IConfigurable
from pip_services4_components.context import IContext
from pip_services4_components.refer import IReferences, IReferenceable
from pip_services4_data.query import DataPage, PagingParams, FilterParams

from .IModelMultiplexorService import IModelMultiplexorService

class ModelMultiplexorService(IModelMultiplexorService, IConfigurable, IReferenceable):

    def configure(self, config: ConfigParams):
        pass

    def set_references(self, references: IReferences):
        pass

    def get_available_models(self, context: Optional[IContext], filter_params: FilterParams,
                   paging: PagingParams) -> DataPage:
        return ['OpenAI ChatGPT 4.5', 'Perplexity Sonar']