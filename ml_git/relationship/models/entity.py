"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import json

from ml_git.constants import DATASET_SPEC_KEY, LABELS_SPEC_KEY, MODEL_SPEC_KEY, STORAGE_SPEC_KEY, V1_STORAGE_KEY


class Entity:
    """Class that's represents an ml-entity.

    Attributes:
        entity_type (str): The type of the ml-entity (datasets, models, labels).
        name (str): The name of the entity.
        private (str): The access of entity metadata.
        metadata_full_name (str): The name of the repository metadata.
        metadata_git_url (str): The git url of the repository metadata.
        metadata_html_url (str): The html url of the repository metadata.
        metadata_owner_name (str): The name of the repository owner.
        metadata_owner_email (str): The email of the repository owner.
        mutability (str): The mutability of the ml-entity (strict|mutable|flexible).
        categories (list): Labels to categorize the entity.
        storage_type (str): The storage type (s3h|azureblobh|gdriveh|sftph).
        storage (dict): The storage configuration.
        version (str): The version of the ml-entity.
    """

    def __init__(self, config, spec_yaml):
        self.__spec = spec_yaml
        self.entity_type = self.__get_entity_type()
        self.name = self.__spec[self.entity_type]['name']
        self.private = False
        self.metadata_full_name = ''
        self.metadata_git_url = ''
        self.metadata_html_url = ''
        self.metadata_owner_name = ''
        self.metadata_owner_email = ''
        self.mutability = self.__spec[self.entity_type]['mutability']
        self.categories = self.__format_categories()
        self.storage_type, self.bucket = self.__get_storage_info()
        self.storage = self.__get_storage(config)
        self.version = self.__spec[self.entity_type]['version']

    def __get_storage(self, config):
        return config.storages.get(self.storage_type, {}).get(self.bucket, {})

    def __get_entity_type(self):
        for entity in [DATASET_SPEC_KEY, LABELS_SPEC_KEY, MODEL_SPEC_KEY]:
            if entity in self.__spec:
                return entity
        return ''

    def __format_categories(self):
        categories = self.__spec[self.entity_type]['categories']
        formatted = [categories] if type(categories) == str else categories
        return formatted

    def __get_storage_info(self):
        manifest = self.__spec[self.entity_type]['manifest']
        storage_key = STORAGE_SPEC_KEY if STORAGE_SPEC_KEY in manifest else V1_STORAGE_KEY
        return manifest[storage_key].split('://')

    def to_dict(self, obj):
        attrs = obj.__dict__.copy()
        for attr in obj.__dict__.keys():
            if attr.startswith('_') or not attrs[attr]:
                del attrs[attr]
        return attrs

    def __repr__(self):
        return json.dumps(self.to_dict(self), indent=2)
