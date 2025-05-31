# coding: utf-8

import json
import pathlib

class Project:
    def __init__(self, path: pathlib.Path, name):
        self.path = path
        self.name = name

        content = json.load(self.path.open('r'))

        self.id = None
        self.tables = None
        self.valid = False
        
        if name in content:
            project = content[name]
            self.id = project['id']
            self.tables = project['tables']
            self.valid = True

    def get_table_id(self, name):
        result = None

        if name in self.tables:
            result = self.tables[name]

        return result

    def is_valid(self) -> bool:
        return self.valid
