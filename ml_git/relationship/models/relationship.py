"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import json

from ml_git.relationship.models.linked_entity import LinkedEntity


class Relationship:
    """Class that's represents an relationship of ml-entity.

    Attributes:
        from_entity (LinkedEntity): The from LinkedEntity of the entity relationship.
        to_entity (LinkedEntity): The to LinkedEntity of the entity relationship.
    """

    def __init__(self, from_entity, to_entity):
        self.from_entity = from_entity
        self.to_entity = to_entity

    def __repr__(self):
        return json.dumps({'from': LinkedEntity.to_dict(self.from_entity),
                           'to': LinkedEntity.to_dict(self.to_entity)}, indent=2)
