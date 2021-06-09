"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""


from ml_git.spec import get_spec_key


class SpecVersion:
    """Class that's represents a ml-entity spec version.

    Attributes:
        tag (str): The tag of the ml-entity spec version.
        version (str): The version of the ml-entity.
        name (str): The name of the ml-entity.
        mutability (str): The mutability of the ml-entity.
        categories (list): Labels to categorize the entity.
        storage (dict): The storage configuration.
        amount (str): The amount of the version files.
        size (str): The size of the version files.
    """

    def __init__(self, spec_tag_yaml):
        self.repo_type = self.__get_repo_type(spec_tag_yaml)
        self.tag = self.__get_tag(spec_tag_yaml)
        self.version = spec_tag_yaml[self.repo_type]['version']
        self.name = spec_tag_yaml[self.repo_type]['name']
        self.mutability = spec_tag_yaml[self.repo_type]['mutability']
        self.categories = spec_tag_yaml[self.repo_type]['categories']
        self.storage = spec_tag_yaml[self.repo_type]['manifest']['storage']
        self.amount = spec_tag_yaml[self.repo_type]['manifest']['amount']
        self.size = spec_tag_yaml[self.repo_type]['manifest']['size']

    def __get_repo_type(spec_tag_yaml):
        return next(iter(spec_tag_yaml))

    def __get_tag(self, metadata):
        sep = '__'
        entity_sepc_key = get_spec_key(self.repo_type)

        cats = metadata[entity_sepc_key]['categories']

        if type(cats) is list:
            categories = sep.join(cats)
        else:
            categories = cats

        return sep.join([categories, metadata[entity_sepc_key]['name']])
