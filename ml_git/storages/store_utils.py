"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import boto3
from botocore.exceptions import ProfileNotFound

from ml_git import log
from ml_git.constants import STORAGE_FACTORY_CLASS_NAME, StorageType, STORAGE_CONFIG_KEY
from ml_git.ml_git_message import output_messages
from ml_git.storages.azure_storage import AzureMultihashStorage
from ml_git.storages.google_drive_storage import GoogleDriveMultihashStorage, GoogleDriveStorage
from ml_git.storages.s3_storage import S3Storage, S3MultihashStorage
from ml_git.storages.sftp_storage import SFtpStorage


def storage_factory(config, storage_string):
    storages = {StorageType.S3.value: S3Storage, StorageType.S3H.value: S3MultihashStorage,
                StorageType.AZUREBLOBH.value: AzureMultihashStorage,
                StorageType.GDRIVEH.value: GoogleDriveMultihashStorage,
                StorageType.GDRIVE.value: GoogleDriveStorage,
                StorageType.SFTPH.value: SFtpStorage}
    sp = storage_string.split('/')
    config_bucket_name, bucket_name = None, None

    try:
        storage_type = sp[0][:-1]
        bucket_name = sp[2]
        config_bucket_name = []
        log.debug(output_messages['DEBUG_STORAGE_AND_BUCKET'] % (storage_type, bucket_name), class_name=STORAGE_FACTORY_CLASS_NAME)
        for k in config[STORAGE_CONFIG_KEY][storage_type]:
            config_bucket_name.append(k)
        if bucket_name not in config_bucket_name:
            log.warn(output_messages['WARN_EXCPETION_CREATING_STORAGE'] % (
                bucket_name, storage_type, config_bucket_name), class_name=STORAGE_FACTORY_CLASS_NAME)
            return None
        bucket = config[STORAGE_CONFIG_KEY][storage_type][bucket_name]
        return storages[storage_type](bucket_name, bucket)
    except ProfileNotFound as pfn:
        log.error(pfn, class_name=STORAGE_FACTORY_CLASS_NAME)
        return None


def get_bucket_region(bucket, credentials_profile=None):
    session = boto3.Session(profile_name=credentials_profile)
    client = session.client(StorageType.S3.value)
    location = client.get_bucket_location(Bucket=bucket)
    if location['LocationConstraint'] is not None:
        region = location['LocationConstraint']
    else:
        region = 'us-east-1'
    return region
