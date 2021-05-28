"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from ml_git.constants import SPEC_EXTENSION
from ml_git.relationship.github_manager import GithubManager
from ml_git.relationship.models.config import Config
from ml_git.relationship.models.entity import Entity
from ml_git.utils import yaml_load_str


class EntityManager:
    """Class that operate over github api to manage entity's operations"""

    MLGIT_CONFIG_FILE = '/.ml-git/config.yaml'

    def __init__(self, github_token, url):
        self._manager = GithubManager(github_token, url)
        self._cache_entities = []

    def __is_config_repo(self, repository):
        """Returns True if the repository contains the file /.ml-git/config.yaml."""
        return self._manager.file_exists(repository, self.MLGIT_CONFIG_FILE)

    def __get_entities_from_config(self, stream):
        """Get entities found in config.yaml

        Args:
            stream (bytes): The stream of config.yaml file.

        Returns:
            list of objects of class Entity.
        """
        config_yaml = yaml_load_str(stream)
        config = Config(config_yaml)
        entities = []
        for remote in config.remotes.values():
            if not remote:
                continue

            repository = self._manager.find_repository(remote)
            for spec_path in self._manager.search_file(repository, SPEC_EXTENSION):
                spec_yaml = yaml_load_str(self._manager.get_file_content(repository, spec_path))
                entity = Entity(config, spec_yaml)
                entity.metadata_full_name = repository.full_name
                entity.metadata_git_url = repository.ssh_url
                entity.private = repository.private
                entity.metadata_html_url = repository.html_url
                entity.metadata_owner_email = repository.owner.email
                entity.metadata_owner_name = repository.owner.name
                for tag in repository.get_tags():
                    content = self._manager.get_file_content(repository, spec_path, tag.name)
                    if not content:
                        continue
                    spec_tag_yaml = yaml_load_str(content)
                    entity.versions.append(Entity(config, spec_tag_yaml))
                entities.append(entity)
        return entities

    def _get_entities_from_config(self, config_path):
        """Get entities found in config.yaml

        Args:
            config_path (str): The absolute path of config.yaml file.

        Returns:
            list of objects of class Entity.
        """
        self._cache_entities = []
        with open(config_path, 'rb') as config:
            self._cache_entities = self.__get_entities_from_config(config)
        return self._cache_entities

    def _get_entities_from_repo(self, repo_name):
        """Get entities found in config.yaml.

         Args:
             repo_name (str): The repository name where is the config.yaml is located in github.

         Returns:
             list of objects of class Entity.
         """
        self._cache_entities = []
        repo = self._manager.find_repository(repo_name)
        if repo is None or self.__is_config_repo(repo) is False:
            return

        config_bytes = self._manager.get_file_content(repo, self.MLGIT_CONFIG_FILE)
        self._cache_entities = self.__get_entities_from_config(config_bytes)

        return self._cache_entities

    def get_entities(self, config_path=None, repo_name=None):
        """Get a list of entities found in config.yaml.

        Args:
            config_path (str): The absolute path of the config.yaml file.
            repo_name (str): The repository name where is the config.yaml is located in github.

        Returns:
            list of class Entity.
        """
        if repo_name:
            return self._get_entities_from_repo(repo_name)
        return self._get_entities_from_config(config_path)