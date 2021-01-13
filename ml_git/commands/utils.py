"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from ml_git.config import config_load
from ml_git.constants import EntityType
from ml_git.log import set_level
from ml_git.repository import Repository

DATASETS = EntityType.DATASETS.value
LABELS = EntityType.LABELS.value
MODELS = EntityType.MODELS.value
PROJECT = 'project'


def init_repository(entity_type='datasets'):
    return Repository(config_load(), entity_type)


repositories = {
    DATASETS: init_repository(DATASETS),
    LABELS: init_repository(LABELS),
    MODELS: init_repository(MODELS),
    PROJECT: init_repository(PROJECT)
}


def set_verbose_mode(ctx, param, value):
    if not value:
        return
    set_level("debug")
