"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import io
from collections import namedtuple

from git import Repo

from ml_git import log
from ml_git._metadata import MetadataManager
from ml_git.config import config_load
from ml_git.constants import SPEC_EXTENSION, FileType, EntityType
from ml_git.relationship.models.entity import Entity
from ml_git.relationship.models.entity_version_relationships import EntityVersionRelationships
from ml_git.relationship.models.linked_entity import LinkedEntity
from ml_git.relationship.models.spec_version import SpecVersion
from ml_git.relationship.utils import export_relationships_to_csv, export_relationships_to_dot
from ml_git.utils import yaml_load_str


class LocalEntityManager:
    """Class that operate over local git repository to manage entity's operations"""

    def __init__(self):
        self._manager = None

    def __init_manager(self, entity_type):
        self._manager = MetadataManager(config_load(), repo_type=entity_type)
        if not self._manager.check_exists():
            self._manager.init()

    def get_entities(self):
        """Get a list of entities found in config.yaml.

        Returns:
            list of class Entity.
        """
        entities = []
        for e_type in EntityType:
            try:
                self.__init_manager(e_type.value)
            except Exception as e:
                log.warn(e)
                continue
            Repository = namedtuple('Repository', ['private', 'full_name', 'ssh_url', 'html_url', 'owner'])
            Owner = namedtuple('Owner', ['email', 'name'])
            repository = Repository(False, '', '', '', Owner('', ''))
            for obj in Repo(self._manager.path).head.commit.tree.traverse():
                if SPEC_EXTENSION in obj.name:
                    entity_spec = yaml_load_str(io.BytesIO(obj.data_stream.read()))
                    entities.append(Entity(repository, entity_spec))

        return entities

    def get_entity_versions(self, name, entity_type):
        """Get a list of spec versions found for an especific entity.

        Args:
            name (str): The name of the entity you want to get the versions.
            entity_type (str): The type of the ml-entity (datasets, models, labels).

        Returns:
            list of class SpecVersion.
        """

        self.__init_manager(entity_type)

        versions = []
        for tag in self._manager.list_tags(name, True):
            content = None
            for obj in tag.commit.tree.traverse():
                if obj.name == name + SPEC_EXTENSION:
                    content = io.BytesIO(obj.data_stream.read())
                    break
            if not content:
                continue

            spec_tag_yaml = yaml_load_str(content)
            spec_version = SpecVersion(spec_tag_yaml)
            versions.append(spec_version)
        return versions

    def get_linked_entities(self, name, version, entity_type):
        """Get a list of linked entities found for an entity version.

        Args:
            name (str): The name of the entity you want to get the linked entities.
            version (str): The version of the entity you want to get the linked entities.
            entity_type (str): The type of the ml-entity (datasets, models, labels).

        Returns:
            list of LinkedEntity.
        """
        self.__init_manager(entity_type)

        for tag in self._manager.list_tags(name, True):
            if tag.name.split('__')[-1] != str(version):
                continue

            content = None
            for obj in tag.commit.tree.traverse():
                if obj.name == name + SPEC_EXTENSION:
                    content = io.BytesIO(obj.data_stream.read())
                    break
            if not content:
                continue

            spec_tag_yaml = yaml_load_str(content)
            entity = SpecVersion(spec_tag_yaml)

            return entity.get_related_entities_info()

    def get_entity_relationships(self, name, entity_type, export_type=FileType.JSON.value, export_path=None):
        """Get a list of relationships for an entity.

        Args:
            name (str): The name of the entity you want to get the linked entities.
            entity_type (str): The type of the ml-entity (datasets, models, labels).
            export_type (str): Set the format of the return (json, csv, dot) [default: json].
            export_path (str): Set the path to export metrics to a file.

        Returns:
            list of EntityVersionRelationships.
        """

        entity_versions = self.get_entity_versions(name, entity_type)
        relationships = {name: []}
        previous_version = None
        for entity_version in entity_versions:
            target_entity = LinkedEntity(entity_version.tag, entity_version.name,
                                         entity_version.version, entity_version.type)
            linked_entities = self.get_linked_entities(target_entity.name, target_entity.version, entity_type)

            if previous_version:
                linked_entities.append(LinkedEntity(previous_version.tag, previous_version.name, previous_version.version, previous_version.type))

            previous_version = target_entity
            relationships[name].append(EntityVersionRelationships(target_entity.version,
                                                                  target_entity.tag, linked_entities))

        if export_type == FileType.CSV.value:
            relationships = export_relationships_to_csv([entity_versions[0]], relationships, export_path)
        elif export_type == FileType.DOT.value:
            relationships = export_relationships_to_dot([entity_versions[0]], relationships, export_path)
        return relationships

    def get_project_entities_relationships(self, export_type=FileType.JSON.value, export_path=None):
        """Get a list of relationships for all project entities.

        Args:
            export_type (str): Set the format of the return [default: json].
            export_path (str): Set the path to export metrics to a file.

        Returns:
            list of EntityVersionRelationships.
        """
        project_entities = self.get_entities()

        all_relationships = {}
        for entity in project_entities:
            e_type = entity.type if entity.type.endswith('s') else '{}s'.format(entity.type)
            entity_relationships = self.get_entity_relationships(entity.name, e_type)
            all_relationships[entity.name] = entity_relationships[entity.name]

        if export_type == FileType.CSV.value:
            all_relationships = export_relationships_to_csv(project_entities, all_relationships, export_path)
        elif export_type == FileType.DOT.value:
            all_relationships = export_relationships_to_dot(project_entities, all_relationships, export_path)

        return all_relationships
