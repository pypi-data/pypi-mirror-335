# -*- coding: utf-8 -*-
"""
    test.IDummyPersistence
    ~~~~~~~~~~~~~~~~~~~~~~
    
    Interface for dummy persistence components
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional, List

from pip_services4_commons.data import AnyValueMap
from pip_services4_components.context import IContext
from pip_services4_data.query import FilterParams, PagingParams, DataPage
from pip_services4_persistence.read import IGetter
from pip_services4_persistence.write import IWriter, IPartialUpdater

from test.fixtures.Dummy import Dummy


class IDummyPersistence(IGetter, IWriter, IPartialUpdater):

    def get_page_by_filter(self, context: Optional[IContext], filter: Optional[FilterParams],
                           paging: Optional[PagingParams]) -> DataPage:
        raise NotImplementedError('Method from interface definition')

    def get_count_by_filter(self, context: Optional[IContext], filter: Optional[FilterParams]) -> int:
        raise NotImplementedError('Method from interface definition')

    def get_one_by_id(self, context: Optional[IContext], id: str) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def get_list_by_ids(self, context: Optional[IContext], ids: List[str]) -> List[Dummy]:
        raise NotImplementedError('Method from interface definition')

    def create(self, context: Optional[IContext], entity: Dummy) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def update(self, context: Optional[IContext], entity) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def update_partially(self, context: Optional[IContext], id: str, data: AnyValueMap) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def delete_by_id(self, context: Optional[IContext], id: str) -> Dummy:
        raise NotImplementedError('Method from interface definition')

    def delete_by_ids(self, context: Optional[IContext], ids: List[str]):
        raise NotImplementedError('Method from interface definition')
