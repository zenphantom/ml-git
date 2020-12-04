"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from click_didyoumean import DYMGroup

from ml_git import admin
from ml_git.commands import help_msg
from ml_git.commands.repository import repository


@repository.group('storage', help='Storage management for this ml-git repository.', cls=DYMGroup)
def storage():
    """
    Storage management for this ml-git repository.
    """
    pass


def check_deprecated_command(context):
    group_name = context.parent.command.name
    deprecated_group = 'store'
    if group_name == deprecated_group:
        print('[WARNING]: Deprecated command, take a look at commands documentation.')


def storage_add(context, **kwargs):
    check_deprecated_command(context)
    admin.store_add(kwargs['type'], kwargs['bucket_name'], kwargs['credentials'],
                    kwargs['global'], kwargs['endpoint_url'])


def storage_del(context, **kwargs):
    check_deprecated_command(context)
    admin.store_del(kwargs['type'], kwargs['bucket_name'], kwargs['global'])
