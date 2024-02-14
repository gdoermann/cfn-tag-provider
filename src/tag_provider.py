import logging

import boto3
from cfn_resource_provider import ResourceProvider

log = logging.getLogger()

request_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "type": "object",
        "required": ["ResourceARN", "Tags"],
        "properties": {
            "ResourceARN": {"type": "array", "items": {"type": "string"}},
            "Tags": {"type": "object"},
        },
    },
}


class TagProvider(ResourceProvider):
    def __init__(self):
        super().__init__()
        self.rg_tagging = boto3.client("resourcegroupstaggingapi")

    @property
    def resource_arns(self):
        return sorted(self.get("ResourceARN"))

    @property
    def old_resource_arns(self):
        return sorted(self.get_old("ResourceARN", self.resource_arns))

    @property
    def tags(self):
        return self.get("Tags")

    @property
    def old_tags(self):
        return self.get_old("Tags", self.tags)

    def has_changes(self):
        return self.resource_arns != self.old_resource_arns or self.tags != self.old_tags

    def check_errors(self, response):
        if response["FailedResourcesMap"]:
            log.error("response %s", response)
            self.fail(response["FailedResourcesMap"][0].get("ErrorMessage"))
            return False
        return True

    def apply_tags(self):
        response = self.rg_tagging.tag_resources(
            ResourceARNList=self.resource_arns, Tags=self.tags
        )
        self.check_errors(response)

    def create(self):
        self.apply_tags()
        self.physical_resource_id = self.logical_resource_id

    def update(self):
        if self.has_changes():
            self.delete_old()
            self.apply_tags()
        else:
            self.success("no changes")

    def delete_old(self):
        keys = list(self.old_tags.keys())
        if keys:
            response = self.rg_tagging.untag_resources(
                ResourceARNList=self.resource_arns, TagKeys=keys
            )
            log.info("Delete Old Tag Response: %s", response)

    def delete(self):
        keys = list(self.tags.keys())
        if keys:
            response = self.rg_tagging.untag_resources(
                ResourceARNList=self.resource_arns, TagKeys=keys
            )
            log.info("Delete Tag Response: %s", response)


provider = TagProvider()


def handler(request, context):
    return provider.handle(request, context)
