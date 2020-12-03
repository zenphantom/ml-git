"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from click_didyoumean import DYMGroup

import ml_git.admin as admin
from ml_git.commands.repository import repository


@repository.group('store', help='[DEPRECATED]: Storage management for this ml-git repository.', cls=DYMGroup)
def store():
    """
    Store management for this ml-git repository.
    """
    pass


def store_add(context, **kwargs):
    admin.store_add(kwargs['type'], kwargs['bucket_name'], kwargs['credentials'],
                    kwargs['global'], kwargs['endpoint_url'])


def store_del(context, **kwargs):
    admin.store_del(kwargs['type'], kwargs['bucket_name'], kwargs['global'])
