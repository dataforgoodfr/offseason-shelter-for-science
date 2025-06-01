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

TokenValidator.regex = re.compile('[a-zA-Z0-9_\-]{40}')

# -----

class Manager:
    def __init__(self, url, project: Project):
        self.url = url
        self.project = project

        self.token = None
        self.mapping = None

    def load_mapping(self, path: pathlib.Path):
        self.mapping = json.load(path.open('r'))

    def list_records(self, table_name):
        result = None

        table_id = self.project.get_table_id(table_name)
        if not table_id:
            raise UnknownTableError()

        headers = self.generate_headers()

        response = requests.get(
            f"{self.url}/api/v2/tables/{table_id}/records",
            headers=headers
        )
        if response.status_code != 200:
            raise APIError(response.status_code, response.json())

        result = response.json()

        return result

    # @todo : test bulk insert and chunks.
    def insert_rows(self, table_name, rows, limit:int=BATCH_INSERT_LIMIT_DEFAULT):
        """
        :param limit: Row limit per request.
        """

        if not rows:
            return

        if limit > BATCH_INSERT_LIMIT_MAX:
            limit = BATCH_INSERT_LIMIT_MAX
        elif limit < 0:
            limit = BATCH_INSERT_LIMIT_DEFAULT

        table_id = self.project.get_table_id(table_name)
        if not table_id:
            raise UnknownTableError()

        headers = self.generate_headers()

        # Chunking rows for bulk insert without exceeding limit.
        chunked_rows = [rows[i:i+limit] for i in range(0, len(rows), limit)]

        print(f'INSERT INTO {table_name}')
        progress = len(chunked_rows) > 1
        for rows in tqdm(chunked_rows):
            response = requests.post(
                f"{self.url}/api/v2/tables/{table_id}/records",
                headers=headers,
                json=rows
            )
            if response.status_code != 200:
                raise APIError(response.status_code, response.json())

    # @todo test different objects
    # @todo test bulk insert
    def insert_objects(self, objects, limit:int=BATCH_INSERT_LIMIT_DEFAULT):
        if not self.mapping:
            raise MappingError("Mapping is not set.")

        object_count = len(objects)
        remaining_count = 0

        rows = {}
        for obj in objects:
            result = self.object_to_row(obj)
            if result:
                (table, row) = result
                if not table in rows:
                    rows[table] = []

                rows[table].append(row)

        # Sending remaining rows
        for table, table_rows in rows.items():
            self.insert_rows(table, table_rows, limit=limit)
            
    def object_to_row(self, obj) -> tuple:
        """
        Transforms an object into a row.

        :return: (<table name>, dict)
        """
        result = None
        
        # Building FQ class name
        obj_type = obj.__module__ + '.' + obj.__class__.__qualname__

        if obj_type in self.mapping:
            obj_info = self.mapping[obj_type]
            fields = obj_info['fields']
            row = {}
            for prop, field in fields.items():
                # Nested object ?
                if '.' in prop:
                    properties = prop.split('.')
                    value = None
                    sub_obj = obj
                    for sub_prop in properties:
                        sub_obj = getattr(sub_obj, sub_prop)
                    row[field] = sub_obj
                else:
                    row[field] = getattr(obj, prop)

            result = (obj_info['table'], row)

        return result

    def generate_headers(self) -> dict:
        return {
            "accept": "application/json",
            "xc-token": self.get_token(),
            "Content-Type": "application/json"
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
