"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from enum import Enum, unique

ROOT_FILE_NAME = '.ml-git'
CONFIG_FILE = '.ml-git/config.yaml'

CONFIG_CLASS_NAME = 'Ml-git Configuration'
METADATA_MANAGER_CLASS_NAME = 'Metadata Manager'
ADMIN_CLASS_NAME = 'Admin'
HASH_FS_CLASS_NAME = 'HashFS'
LOCAL_REPOSITORY_CLASS_NAME = 'Local Repository'
MULTI_HASH_CLASS_NAME = 'Multihash'
STORAGE_FACTORY_CLASS_NAME = 'StorageFactory'
METADATA_CLASS_NAME = 'Metadata'
POOL_CLASS_NAME = 'Pool'
REFS_CLASS_NAME = 'Refs'
REPOSITORY_CLASS_NAME = 'Repository'
ML_GIT_PROJECT_NAME = 'Ml-git Project'
SFTPSTORE_NAME = 'SFtpStorage'
S3STORAGE_NAME = 'S3Storage'
AZURE_STORAGE_NAME = 'AzureMultihashStorage'
S3_MULTI_HASH_STORAGE_NAME = 'S3MultihashStorage'
MULTI_HASH_STORAGE_NAME = 'MultihashStorage'
HEAD = 'HEAD'
HEAD_1 = 'HEAD~1'
FAKE_STORAGE = 'fake_storage'
FAKE_TYPE = 's3h'
BATCH_SIZE = 'batch_size'
PUSH_THREADS_COUNT = 'push_threads_count'
BATCH_SIZE_VALUE = 20
RGX_ADDED_FILES = r'[+]\s+(.*)[:]\s+null'
RGX_DELETED_FILES = r'[-]\s+(.*)[:]\s+null'
RGX_SIZE_FILES = r'[+]\s+size:\s+(\d+(?:[.]\d+)*\s+.+)'
RGX_AMOUNT_FILES = r'[+]\s+amount:\s+(\d+)'
RGX_TAG_FORMAT = r'(?:[^_]+_{2}){2,}\d+$'
ADDED = 'Added files'
DELETED = 'Deleted files'
AUTHOR = 'Author'
EMAIL = 'Email'
DATE = 'Date'
MESSAGE = 'Message'
SIZE = 'Files size'
AMOUNT = 'Amount of files'
TAG = 'Tag'
GDRIVE_STORAGE = 'GoogleDriveStorage'
GLOBAL_ML_GIT_CONFIG = '.mlgitconfig'
STORAGE_LOG = 'storage.log'
SPEC_EXTENSION = '.spec'
MANIFEST_FILE = 'MANIFEST.yaml'
INDEX_FILE = 'INDEX.yaml'
DEFAULT_BRANCH_FOR_EMPTY_REPOSITORY = 'master'
PERFORMANCE_KEY = 'metrics'
STORAGE_KEY = 'storage'
V1_STORAGE_KEY = 'store'
V1_DATASETS_KEY = 'dataset'
V1_MODELS_KEY = 'model'
MANIFEST_KEY = 'manifest'
STATUS_NEW_FILE = 'New file: '
STATUS_DELETED_FILE = 'Deleted: '
RELATED_DATASET_TABLE_INFO = 'Related dataset - (version)'
RELATED_LABELS_TABLE_INFO = 'Related labels - (version)'


class Mutability(Enum):
    STRICT = 'strict'
    FLEXIBLE = 'flexible'
    MUTABLE = 'mutable'

    @staticmethod
    def list():
        return list(map(lambda c: c.value, Mutability))


@unique
class StorageType(Enum):
    S3 = 's3'
    S3H = 's3h'
    AZUREBLOBH = 'azureblobh'
    GDRIVEH = 'gdriveh'
    GDRIVE = 'gdrive'
    SFTPH = 'sftph'

    @staticmethod
    def to_list():
        return [storage.value for storage in StorageType]


@unique
class EntityType(Enum):
    DATASETS = 'datasets'
    LABELS = 'labels'
    MODELS = 'models'

    @staticmethod
    def to_list():
        return [entity.value for entity in EntityType]


@unique
class FileType(Enum):
    CSV = 'csv'
    JSON = 'json'

    @staticmethod
    def to_list():
        return [file.value for file in FileType]
