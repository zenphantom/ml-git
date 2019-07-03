"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
from pathlib import Path

import yaml

from repository.MLGitRepositoryConfiguration import MLGitRepositoryConfiguration
from utils.constants import *


def get_repository_root():
    current_path = Path(os.getcwd())

    while current_path is not None:
        try:
            next(current_path.glob(CONFIG_FILE))
            return current_path
        except StopIteration:
            parent = current_path.parent
            if parent == current_path:
                return None
            else:
                current_path = parent
    return None


def is_running_from_repository():
    return get_repository_root() is not None


def assert_running_from_repository():
    if not is_running_from_repository():
        raise Exception('You are not inside a managed ML-Git directory.')


def create_repository_configuration_file(path, name, version, labels, data_store):
    config = MLGitRepositoryConfiguration(name=name, version=version, labels=labels, data_store=data_store)
    full_path = os.path.join(path, CONFIG_FILE)
    with open(full_path, 'w') as out:
        out.write(yaml.safe_dump(config.__dict__))
