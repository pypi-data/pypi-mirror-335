# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Optional

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams

class IModelMultiplexorService(ABC):

    @abstractmethod
    def get_available_models(self, context: Optional[IContext], filter_params: FilterParams, paging: PagingParams) -> DataPage:
        raise NotImplementedError("Method is not implemented")