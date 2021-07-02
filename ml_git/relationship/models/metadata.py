"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import json


class Metadata:
    """Class that represents an ml-entity metadata.

    Attributes:
        full_name (str): The full name of the metadata.
        git_url (str): The git url of the metadata.
        html_url (str): The html url of the metadata.
        owner_email (str): The owner email of the ml-entity metadata.
        owner_name (str): The owner name of the ml-entity metadata.
    """

    def __init__(self, repository):
        self.full_name = repository.full_name
        self.git_url = repository.ssh_url
        self.html_url = repository.html_url
        self.owner_email = repository.owner.email
        self.owner_name = repository.owner.name

    @staticmethod
    def to_dict(obj):
        attrs = obj.__dict__.copy()
        for attr in obj.__dict__.keys():
            if attr.startswith('_') or not attrs[attr]:
                del attrs[attr]
        return attrs

    def __repr__(self):
        return json.dumps(self.to_dict(self), indent=2)
