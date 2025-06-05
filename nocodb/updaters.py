# coding: utf-8

import abc

from .api import Manager
from .tables import *

from tqdm import tqdm

import datagov.ckan.resource


class AbstractUpdater(abc.ABC):
    def __init__(self, api_mgr: Manager, pk="Id"):
        self.api_mgr = api_mgr
        self.pk = pk

        self.fields = self._get_fields()

        # Primary key check done once during init.
        if not self.pk in self.fields:
            self.fields.append(self.pk)

        self.print_update_objects = False
        self.print_where = False

        self.initialize()

    def initialize(self):
        pass

    def dispose(self):
        pass

    def get_fields(self) -> list:
        return self.fields

    def get_sort_field(self) -> str:
        return "dg_id"

    def update(self, where=None):
        is_last_page = False

        offset = 0

        table_name = self.get_table_name()

        count = self.api_mgr.count_records(table_name, where=where)
        if not count:
            return

        progress = tqdm(total=count) if count > 2000 else None

        message = f"UPDATING {table_name}"
        if where and self.print_where:
            message += f" WHERE {where}"

        print(message, f"({count})")

        while not is_last_page:
            list_result = self.api_mgr.list_records(
                table_name,
                fields=self.get_fields(),
                limit=1000,
                offset=offset,
                sort=self.get_sort_field(),
                where=where,
            )
            is_last_page = list_result.page_info.is_last_page

            update_objects = []

            for record in list_result.next():
                update_obj = self.parse_record(record)
                if update_obj:
                    if not self.pk in update_obj.keys():
                        update_obj[self.pk] = record[self.pk]

                    if self.print_update_objects:
                        print(update_obj)

                    update_objects.append(update_obj)

            result_count = list_result.count()
            offset += result_count
            if progress:
                progress.update(result_count)

            if update_objects:
                self.api_mgr.update_records(self.get_table_name(), update_objects)

        if progress:
            progress.close()
        self.dispose()

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


class DatasetAccessUpdater(AbstractUpdater):
    """Should not be instanciated directly."""

    def initialize(self):
        self.counts = {}
        self.current_dataset_id = None

        # self.print_update_objects = True

    def dispose(self):
        self.counts = {}

    def get_table_name(self) -> str:
        return TABLE_DG_DATASETS

    def _get_fields(self) -> list:
        return ["dg_id"]

    def add_dataset(self, dataset_id):
        self.current_dataset_id = dataset_id
        self.counts[dataset_id] = {"ddl": 0, "dir": 0, "unk": 0, "empty": 0}

    def get_dataset_count(self) -> int:
        return len(self.counts)

    def generate_where_from_datasets(self) -> str:
        return "~or".join(
            [f"(dg_id,eq,{dataset_id})" for dataset_id in self.counts.keys()]
        )

    def inc_direct_download_count(self, dataset_id):
        self.counts[dataset_id]["ddl"] += 1

    def inc_directory_count(self, dataset_id):
        self.counts[dataset_id]["dir"] += 1

    def inc_unknown_count(self, dataset_id):
        self.counts[dataset_id]["unk"] += 1

    def inc_empty_count(self, dataset_id):
        self.counts[dataset_id]["empty"] += 1

    def parse_record(self, record) -> dict:
        result = {}

        dataset_id = record["dg_id"]
        if self.counts[dataset_id] and self.counts[dataset_id]["ddl"]:
            result["access_directdl_count"] = self.counts[dataset_id]["ddl"]

        if self.counts[dataset_id] and self.counts[dataset_id]["dir"]:
            result["access_directory_count"] = self.counts[dataset_id]["dir"]

        if self.counts[dataset_id] and self.counts[dataset_id]["unk"]:
            result["access_unknown_count"] = self.counts[dataset_id]["unk"]

        if self.counts[dataset_id] and self.counts[dataset_id]["empty"]:
            result["access_empty_count"] = self.counts[dataset_id]["empty"]

        if not result:
            result = None
        else:
            total = 0
            for count in result.values():
                total += count
            result["access_total_count"] = total

        return result


# -----


class ResourceTypeUpdater(AbstractUpdater):
    def initialize(self):
        self.last_dataset_id = None
        self.dataset_acccess_updater = DatasetAccessUpdater(self.api_mgr)

        # self.print_update_objects = True

    def dispose(self):
        self.update_dataset_access()

    def update_dataset_access(self):
        # Updating for current batch of datasets
        self.dataset_acccess_updater.update(
            where=self.dataset_acccess_updater.generate_where_from_datasets()
        )

    def get_table_name(self) -> str:
        return TABLE_DG_RESOURCES

    def get_sort_field(self) -> str:
        return "dg_dataset_id"

    def _get_fields(self) -> list:
        return ["dg_dataset_id", "dg_url"]

    def parse_record(self, record) -> dict:
        res_type = None

        # Records are sorted by dataset id.
        if self.last_dataset_id != record["dg_dataset_id"]:
            # Batch dataset update when sufficient number reached
            if (
                self.last_dataset_id
                and self.dataset_acccess_updater.get_dataset_count() > 100
            ):
                self.update_dataset_access()

            self.last_dataset_id = record["dg_dataset_id"]
            self.dataset_acccess_updater.add_dataset(self.last_dataset_id)

        ckan_res_type = datagov.ckan.resource.Resource.get_type_from_url(
            record["dg_url"]
        )

        res_type = ckan_res_type.to_db_value()

        if not res_type:
            self.dataset_acccess_updater.inc_unknown_count(self.last_dataset_id)

        result = {"resource_type": res_type}

        return result


# -----
