"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import json


class Relationship:
    """Class that's represents an relationship of ml-entity.

    Attributes:
        from (LinkedEntity): The from LinkedEntity of the entity relationship.
        to (LinkedEntity): The to LinkedEntity of the entity relationship.
    """

    def __init__(self, from, to):
        self.from = from
        self.to = to

    @staticmethod
    def to_dict(obj):
        attrs = obj.__dict__.copy()
        for attr in obj.__dict__.keys():
            if attr.startswith('_') or not attrs[attr]:
                del attrs[attr]
        return attrs

    def __repr__(self):
        return json.dumps(self.to_dict(self), indent=2)
