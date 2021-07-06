"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from click_didyoumean import DYMGroup

from ml_git import admin
from ml_git.commands.repository import repository


@repository.group('storage', help='Storage management for this ml-git repository.', cls=DYMGroup)
def storage():
    """
    Storage management for this ml-git repository.
    """
    pass


def storage_add(context, **kwargs):
    sftp_configs = {'username': kwargs['username'],
                    'private_key': kwargs['private_key'],
                    'port': kwargs['port']}
    admin.storage_add(storage_type=kwargs['type'], bucket=kwargs['bucket_name'], credentials_profile=kwargs['credentials'],
                      global_conf=kwargs['global'], endpoint_url=kwargs['endpoint_url'],
                      sftp_configs=sftp_configs, region=kwargs['region'])


def storage_del(context, **kwargs):
    admin.storage_del(kwargs['type'], kwargs['bucket_name'], kwargs['global'])
