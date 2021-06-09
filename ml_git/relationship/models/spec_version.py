"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import json

from ml_git.constants import DATASET_SPEC_KEY, LABELS_SPEC_KEY, MODEL_SPEC_KEY, STORAGE_SPEC_KEY, V1_STORAGE_KEY


class SpecVersion:
    """Class that's represents a ml-entity spec version.

    Attributes:
        tag (str): The tag of the ml-entity spec version.
        version (str): The version of the ml-entity.
        mutability (str): The mutability of the ml-entity.
        categories (list): Labels to categorize the entity.
        storage (dict): The storage configuration.
        amount (str): The amount of the version files.
        size (str): The size of the version files.
    """

    def __init__(self, spec_tag_yaml):
        self.__spec = spec_tag_yaml
        self.entity_type = self.__get_entity_type()
        self.name = spec_tag_yaml[self.entity_type]['name']

        self.version = spec_tag_yaml[self.entity_type]['version']
        self.tag = self.__get_tag(spec_tag_yaml)
        self.mutability = spec_tag_yaml[self.entity_type]['mutability']
        self.categories = self.__format_categories()
        self.storage_type, self.bucket = self.__get_storage_info()
        self.amount = spec_tag_yaml[self.entity_type]['manifest']['amount']
        self.size = spec_tag_yaml[self.entity_type]['manifest']['size']

    def __get_entity_type(self):
        for entity in [DATASET_SPEC_KEY, LABELS_SPEC_KEY, MODEL_SPEC_KEY]:
            if entity in self.__spec:
                return entity
        return ''

    def __format_categories(self):
        categories = self.__spec[self.entity_type]['categories']
        formatted = [categories] if type(categories) == str else categories
        return formatted

    def __get_tag(self, metadata):
        sep = '__'

        cats = metadata[self.entity_type]['categories']

        if type(cats) is list:
            categories = sep.join(cats)
        else:
            categories = cats

        return sep.join([categories, metadata[self.entity_type]['name'], str(self.version)])

    def __get_storage_info(self):
        manifest = self.__spec[self.entity_type]['manifest']
        storage_key = STORAGE_SPEC_KEY if STORAGE_SPEC_KEY in manifest else V1_STORAGE_KEY
        return manifest[storage_key].split('://')

    def to_dict(self, obj):
        attrs = obj.__dict__.copy()
        ignore_attributes = ['entity_type', 'name']
        for attr in obj.__dict__.keys():
            if attr.startswith('_') or not attrs[attr] or attr in ignore_attributes:
                del attrs[attr]
        return attrs

    def __repr__(self):
        return json.dumps(self.to_dict(self), indent=2)
