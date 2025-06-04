# coding: utf-8

import abc

from .api import Manager
from .tables import *

class AbstractUpdater(abc.ABC):
    def __init__(self, api_mgr: Manager, pk='Id'):
        self.api_mgr = api_mgr
        self.pk = pk

        self.fields = self._get_fields()

        # Primary key check done once during init.
        if not self.pk in self.fields:
            self.fields.append(self.pk)

        self.initialize()

    def initialize(self):
        pass

    def get_fields(self)-> list:
        return self.fields

    def update(self, where=None):
        is_last_page = False

        offset = 0

        table_name = self.get_table_name()

        count = self.api_mgr.count_records(table_name, where=where)
        
        print(count)
        
        while not is_last_page:
            list_result = self.api_mgr.list_records(
                table_name,
                fields=self.get_fields(),
                limit=1000,
                offset=offset,
                sort='dg_dataset_id',
                where=where,
                )
            is_last_page = list_result.page_info.is_last_page

            update_objects = []

            for record in list_result.next():
                update_obj = self.parse_record(record)
                if update_obj:
                    if not self.pk in update_obj.keys():
                        update_obj[self.pk] = record[self.pk]
                    update_objects.append(update_obj)
                
            offset += list_result.count()
            
            if update_objects:
                print(self.api_mgr.update_records(self.get_table_name(), update_objects))

    @abc.abstractmethod
    def get_table_name(self) -> str:
        pass

    @abc.abstractmethod
    def _get_fields(self) -> list:
        """Returns the list of field required for parse_record operation."""
        pass

    @abc.abstractmethod
    def parse_record(self, record) -> dict:
        """
        Parse a record as returned by "List Table Records" API method and returns an object to be passed to "Update Table Records" API method.
        :return: dict
        """
        pass

# -----

class ResourceTypeUpdater(AbstractUpdater):
    def initialize(self):
        self.last_dataset_id = None

    def get_table_name(self) -> str:
        return TABLE_DG_RESOURCES

    def _get_fields(self) -> list:
        return ['dg_dataset_id', 'dg_url']

    def parse_record(self, record) -> dict:
        res_type = None

        if self.last_dataset_id != record['dg_dataset_id']:
            ...

        url = record['dg_url']
        if url:
            if url[-1] == '/':
                res_type = 'directory'

            if '.' in url:
                ext = url.split('.')[-1]
                if len(ext) <= 5:
                    res_type = ext

        if res_type:
            return {'resource_type': res_type}
        
        return None

# -----
