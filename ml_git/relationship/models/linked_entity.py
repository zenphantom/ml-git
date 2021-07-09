"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import json


class LinkedEntity:
    """Class that represents a linked ml-entity.

    Attributes:
        name (str): The name of the entity.
        type (str): The type of the ml-entity (datasets, models, labels).
        version (str): The version of the ml-entity.
        tag (str): The tag of the ml-entity spec version.
    """

    def __init__(self, tag, name, version, type):
        self.tag = tag
        self.name = name
        self.version = version
        self.type = type

    @staticmethod
    def to_dict(obj):
        attrs = obj.__dict__.copy()
        for attr in obj.__dict__.keys():
            if attr.startswith('_') or not attrs[attr]:
                del attrs[attr]
        return attrs

    def __repr__(self):
        return json.dumps(self.to_dict(self), indent=2)
