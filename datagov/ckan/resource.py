# coding: utf-8

import abc
from urllib.parse import urlparse
import re

_FILE_EXT_REGEX = re.compile(r".+\.([a-zA-Z7][a-zA-Z0-9]+)$")
_OTHER_AUTHORIZED_EXTENSIONS = ["geojson"]
_REJECTED_EXTENSIONS = ["aspx", "htm", "html", "htmlx", "shtml"]


class Type(abc.ABC):
    pass


class Empty(Type):
    def to_db_value(self):
        return None


class Directory(Type):
    def to_db_value(self):
        return "dir"


class WebPage(Type):
    def to_db_value(self):
        return "web"


class File(Type):
    def __init__(self, ext):
        self.ext = ext

    def to_db_value(self):
        return self.ext


class Resource:
    def __init__(self, obj):
        self.obj = obj

        self.id = obj["id"]
        self.name = obj["name"]
        self.description = obj["description"]

        self.resource_locator_function = (
            obj["resource_locator_function"]
            if "resource_locator_function" in obj
            else None
        )
        self.resource_locator_protocol = (
            obj["resource_locator_protocol"]
            if "resource_locator_protocol" in obj
            else None
        )

        self.mimetype = None
        if "mimetype" in obj:
            self.mimetype = obj["mimetype"]

        self.state = obj["state"]
        self.created = obj["created"]
        self.metadata_modified = obj["metadata_modified"]
        self.url = obj["url"]
        self.resource_type = self.get_type_from_url(self.url).to_db_value()

        self.dataset_id = obj["package_id"]

    @staticmethod
    def get_type_from_url(url):
        result = None

        if not url or not url.strip():
            return Empty()

        parsed_url = urlparse(url)

        url_path = parsed_url.path.strip()
        if url_path:
            if url_path[-1] == "/" or url_path.endswith("%2F"):
                result = Directory()
            else:
                match_res = _FILE_EXT_REGEX.match(url_path)
                if match_res:
                    ext = match_res.group(1)
                    if (
                        len(ext) <= 5 and ext not in _REJECTED_EXTENSIONS
                    ) or ext in _OTHER_AUTHORIZED_EXTENSIONS:
                        result = File(ext)

        if not result:
            result = WebPage()

        return result
