"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from ml_git.constants import STORAGE_CONFIG_KEY, V1_STORAGE_KEY, EntityType, V1_DATASETS_KEY, V1_MODELS_KEY
from ml_git.relationship.utils import get_repo_name_from_url, format_storages


class Config:

    def __init__(self, config_yaml):
        self.config = config_yaml
        self.remotes = dict()
        self.storages = dict()
        self.parse_config()

    def parse_config(self):
        storage_config_key = STORAGE_CONFIG_KEY if STORAGE_CONFIG_KEY in self.config else V1_STORAGE_KEY
        dataset_key =  EntityType.DATASETS.value if EntityType.DATASETS.value in self.config else V1_DATASETS_KEY
        model_key = EntityType.MODELS.value if EntityType.MODELS.value in self.config else V1_MODELS_KEY
        self.remotes[dataset_key] = get_repo_name_from_url(self.config[dataset_key]['git']) if dataset_key in self.config else ''
        self.remotes[EntityType.LABELS.value] = get_repo_name_from_url(self.config[EntityType.LABELS.value]['git']) if EntityType.LABELS.value in self.config else ''
        self.remotes[model_key] = get_repo_name_from_url(self.config[model_key]['git']) if model_key in self.config else ''
        self.storages = format_storages(self.config[storage_config_key])
