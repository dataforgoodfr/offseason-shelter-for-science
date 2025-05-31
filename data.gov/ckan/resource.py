# coding: utf-8

class Resource:
    def __init__(self, obj):
        self.obj = obj

        self.id = obj['id']
        self.name = obj['name']
        self.description = obj['description']
        self.resource_locator_function = obj['resource_locator_function']
        self.resource_locator_protocol = obj['resource_locator_protocol']
        self.state = obj['state']
        self.created = obj['created']
        self.metadata_modified = obj['metadata_modified']
        self.url = obj['url']

        self.dataset_id = obj['package_id']