"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""


class Version:
    """Class that's represents a ml-entity version.

    Attributes:
        tag (str): The tag of the ml-entity version.
        version (str): The version of the ml-entity.
        categories (list): Labels to categorize the entity.
        mlgit_version (str): The version of the ml-git.
        storage (dict): The storage configuration.
        amount (str): The amount of the version files.
        size (str): The size of the version files.
    """

    def __init__(self, tag, version, categories, mlgit_version, storage, amount, size):
        self.tag = tag
        self.version = version
        self.categories = categories
        self.mlgit_version = mlgit_version
        self.storage = storage
        self.amount = amount
        self.size = size
