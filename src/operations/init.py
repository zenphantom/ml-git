"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from repository.ml_git_reposotory import *


def handle_init_operation(dataset_source_dir='ml-git-data-source'):
    if is_running_from_repository():
        raise Exception('Cannot initialize a ML-Git repository. You are already inside a managed ML-Git repository.')
    else:
        print('Creating repo')
