# coding: utf-8

from .organization import Organization
from .resource import Resource


class Dataset:
    def __init__(self, obj, load_resources=False):
        self.obj = obj

        self.id = obj["id"]
        self.title = obj["title"]
        self.name = obj["name"]
        self.notes = obj["notes"]
        self.state = obj["state"]
        self.metadata_created = obj["metadata_created"]
        self.metadata_modified = obj["metadata_modified"]

        self.access_directdl_count = 0
        self.access_total_count = 0

        self.resources = {}

        if load_resources and "resources" in obj:
            for resource in obj["resources"]:
                resource = Resource(resource)

                if resource.id in self.resources:
                    raise Exception("Resource duplicate:", resource.id)

                self.resources[resource.id] = resource

                if resource.resource_type:
                    self.access_total_count += 1

                    if resource.resource_type not in ["web", "dir"]:
                        self.access_directdl_count += 1

        self.organization = Organization(obj["organization"])
