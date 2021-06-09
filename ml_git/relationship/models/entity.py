"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import json

from ml_git.relationship.models.spec_version import SpecVersion


class Entity:
    """Class that's represents an ml-entity.

    Attributes:
        name (str): The name of the entity.
        entity_type (str): The type of the ml-entity (datasets, models, labels).
        private (str): The access of entity metadata.
        metadata_full_name (str): The name of the repository metadata.
        metadata_git_url (str): The git url of the repository metadata.
        metadata_html_url (str): The html url of the repository metadata.
        metadata_owner_name (str): The name of the repository owner.
        metadata_owner_email (str): The email of the repository owner.
        last_spec_version (SpecVersion): The spec file of entity last version.
    """

    def __init__(self, repository, spec_yaml):
        self.last_spec_version = SpecVersion(spec_yaml)
        self.name = self.last_spec_version.name
        self.entity_type = self.last_spec_version.entity_type
        self.metadata_full_name = repository.full_name
        self.metadata_git_url = repository.ssh_url
        self.private = repository.private
        self.metadata_html_url = repository.html_url
        self.metadata_owner_email = repository.owner.email
        self.metadata_owner_name = repository.owner.name

    def to_dict(self, obj):
        attrs = obj.__dict__.copy()
        ignore_attributes = ['last_spec_version']
        for attr in obj.__dict__.keys():
            if attr.startswith('_') or not attrs[attr] or attr in ignore_attributes:
                del attrs[attr]
        attrs['last_spec_version'] = self.last_spec_version.to_dict(self.last_spec_version)
        return attrs

    def __repr__(self):
        return json.dumps(self.to_dict(self), indent=2)
