# coding: utf-8

import getpass
import json
import pathlib
import re

import requests
from tqdm import tqdm

from .project import Project

BATCH_INSERT_LIMIT_DEFAULT = 2000
BATCH_INSERT_LIMIT_MAX = 5000


class TokenError(Exception):
    pass


class UnknownTableError(Exception):
    pass


class MappingError(Exception):
    pass


class APIError(Exception):
    pass


# -----


class TokenValidator:
    def __init__(self, token):
        self.valid = True
        match_res = self.regex.match(token)
        if match_res:
            self.valid = True

    def is_valid(self) -> bool:
        return self.valid


TokenValidator.regex = re.compile("[a-zA-Z0-9_\-]{40}")

# -----


class PageInfo:
    def __init__(self, page_info):
        self.total_rows = page_info["totalRows"]

        self.page = page_info["page"]
        self.page_size = page_info["pageSize"]

        self.is_first_page = page_info["isFirstPage"]
        self.is_last_page = page_info["isLastPage"]


class ListResult:
    def __init__(self, response):
        self.list = response["list"]
        self.page_info = PageInfo(response["pageInfo"])

    def next(self):
        for record in self.list:
            yield record

    def count(self):
        return len(self.list)


# -----


# @todo : Caching URL by HTTP method and table name ?
class Manager:
    def __init__(self, url, project: Project):
        self.url = url
        self.project = project

        self.token = None
        self.mapping = None

    def load_mapping(self, path: pathlib.Path):
        self.mapping = json.load(path.open("r"))

    def count_records(self, table_name, where=None) -> int:
        response = self.table_request(
            "get",
            table_name,
            url_suffix="/count",
            where=where,
        )
        return response["count"]

    def list_records(
        self,
        table_name,
        fields: list = None,
        limit=None,
        offset=None,
        sort=None,
        where=None,
    ):
        """
        :return: ListResult
        """
        result = None

        response = self.table_request(
            "get",
            table_name,
            fields=fields,
            limit=limit,
            offset=offset,
            sort=sort,
            where=where,
        )

        return ListResult(response)

    def update_records(self, table_name, update_objects):
        return self.table_request(
            "patch",
            table_name,
            json=update_objects,
        )

    # @todo : test bulk insert and chunks.
    def create_records(
        self, table_name, records, limit: int = BATCH_INSERT_LIMIT_DEFAULT
    ):
        """
        :param limit: Record limit per request.
        """

        if not records:
            return

        if limit > BATCH_INSERT_LIMIT_MAX:
            limit = BATCH_INSERT_LIMIT_MAX
        elif limit < 0:
            limit = BATCH_INSERT_LIMIT_DEFAULT

        # Chunking records for bulk insert without exceeding limit.
        chunked_records = [
            records[i : i + limit] for i in range(0, len(records), limit)
        ]

        progress = len(chunked_records) > 1

        print(f"INSERT INTO {table_name}")
        for records in tqdm(chunked_records):
            response = self.table_request("post", table_name, json=records)

    # @todo test different objects
    # @todo test bulk insert
    def create_records_from_objects(
        self, objects, limit: int = BATCH_INSERT_LIMIT_DEFAULT
    ):
        if not self.mapping:
            raise MappingError("Mapping is not set.")

        object_count = len(objects)
        remaining_count = 0

        records = {}
        for obj in objects:
            result = self.object_to_row(obj)
            if result:
                (table, row) = result
                if not table in records:
                    records[table] = []

                records[table].append(row)

        # Sending remaining records
        for table, table_records in records.items():
            self.create_records(table, table_records, limit=limit)

    def object_to_row(self, obj) -> tuple:
        """
        Transforms an object into a row.

        :return: (<table name>, dict)
        """
        result = None

        # Building FQ class name
        obj_type = obj.__module__ + "." + obj.__class__.__qualname__

        if obj_type in self.mapping:
            obj_info = self.mapping[obj_type]
            fields = obj_info["fields"]
            row = {}
            for prop, field in fields.items():
                # Nested object ?
                if "." in prop:
                    properties = prop.split(".")
                    value = None
                    sub_obj = obj
                    for sub_prop in properties:
                        sub_obj = getattr(sub_obj, sub_prop)
                    row[field] = sub_obj
                else:
                    row[field] = getattr(obj, prop)

            result = (obj_info["table"], row)

        return result

    def get_table_url(self, table_name, suffix=None):
        table_id = self.project.get_table_id(table_name)
        if not table_id:
            raise UnknownTableError()

        result = f"{self.url}/api/v2/tables/{table_id}/records"

        if suffix:
            result += suffix

        return result

    def table_request(self, method, table_name, url_suffix=None, **kwargs):
        return self.request(
            method,
            self.get_table_url(table_name, suffix=url_suffix),
            **kwargs,
        )

    def request(self, method, url, **kwargs):
        method = getattr(requests, method)

        params = {}
        print(kwargs)
        if "fields" in kwargs:
            params["fields"] = ",".join(kwargs["fields"])
        if "limit" in kwargs:
            params["limit"] = kwargs["limit"]
        if "offset" in kwargs:
            params["offset"] = kwargs["offset"]
        if "sort" in kwargs:
            params["sort"] = kwargs["sort"]
        if "where" in kwargs:
            params["where"] = kwargs["where"]

        if not params:
            params = None

        json = kwargs["json"] if "json" in kwargs else None

        response = method(
            url, headers=self.generate_headers(), params=params, json=json
        )
        if response.status_code != 200:
            raise APIError(response.status_code, response.json())

        return response.json()

    def generate_headers(self) -> dict:
        return {
            "accept": "application/json",
            "xc-token": self.get_token(),
            "Content-Type": "application/json",
        }

    def get_token(self) -> str:
        """
        @todo Security issue : token can be read in memory.
        """
        if self.token:
            return self.token

        result = None

        retries = 3
        while retries:
            result = getpass.getpass("NOCODB API token : ").strip()

            if not TokenValidator(result).is_valid():
                retries -= 1
                print("Empty or bad token !")
                if not retries:
                    raise TokenError()
            else:
                self.token = result
                break

        return result
