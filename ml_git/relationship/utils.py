"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import urllib

from ml_git.utils import yaml_load_str


def is_minio_storage(storage):
    """Returns True if the endpoint-url field is present and is not null."""
    return 'endpoint-url' in storage and storage['endpoint-url']


def format_storages(storages):
    """Augment existing storage information with server type, etc."""
    try:
        for bucket_type, buckets in storages.items():
            for bucket_name, bucket in buckets.items():
                bucket['name'] = bucket_name
                bucket['type'] = bucket_type
                bucket['subtype'] = ''
                if bucket_type in ('s3', 's3h'):
                    bucket['subtype'] = 'minio' if is_minio_storage(bucket) else 'aws'
    except Exception:
        print('Error augmenting storage information')
    return storages


def get_repo_name_from_url(repository_url: str) -> str:
    """Returns the Github repository full name from a git url or usual url format string."""
    if '://' in repository_url:
        return urllib.parse.urlparse(repository_url).path[1:].replace('.git', '')
    return repository_url.replace('.git', '').split(':')[-1]


def get_empty_config():
    doc = '''
      storages:
        s3:
          dummy-bucket:
            aws-credentials:
              profile: None
            region: us-east-1
    '''
    c = yaml_load_str(doc)
    return c
