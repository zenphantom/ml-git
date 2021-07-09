"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import json

from ml_git.relationship.models.linked_entity import LinkedEntity


class EntityVersionRelationships:
    """Class that represents the relationships of an ml-entity in a specified version.

    Attributes:
        version (str): The version of the ml-entity.
        tag (str): The tag of the ml-entity.
        relationships (list): List of linked entities of the ml-entity in the specified version.
    """

    def __init__(self, entity_version, entity_tag, linked_entities):
        self.version = entity_version
        self.tag = entity_tag
        self.relationships = linked_entities

    def __repr__(self):
        output = {'version': self.version,
                  'tag': self.tag,
                  'relationships': []}
        for entity in self.relationships:
            output['relationships'].append(LinkedEntity.to_dict(entity))
        return json.dumps(output, indent=2)
