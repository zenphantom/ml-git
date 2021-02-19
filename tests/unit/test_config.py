"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil
import unittest
from unittest import mock

import pytest

from ml_git.admin import init_mlgit
from ml_git.config import validate_config_spec_hash, get_sample_config_spec, get_sample_spec, \
    validate_spec_hash, config_verbose, get_refs_path, config_load, mlgit_config_load, list_repos, \
    get_index_path, get_objects_path, get_cache_path, get_metadata_path, import_dir, \
    extract_storage_info_from_list, create_workspace_tree_structure, get_batch_size, merge_conf, \
    merge_local_with_global_config, mlgit_config, save_global_config_in_local, start_wizard_questions
from ml_git.constants import BATCH_SIZE_VALUE, BATCH_SIZE, Mutability, STORAGE_KEY, EntityType, StorageType
from ml_git.utils import get_root_path, yaml_load

DATASETS = EntityType.DATASETS.value
LABELS = EntityType.LABELS.value
MODELS = EntityType.MODELS.value
STRICT = Mutability.STRICT.value
S3H = StorageType.S3H.value
S3 = StorageType.S3.value
GDRIVEH = StorageType.GDRIVEH.value


class ConfigTestCases(unittest.TestCase):

    def test_validate_config_spec_hash(self):
        # Success case
        spec = get_sample_config_spec('somebucket', 'someprofile', 'someregion')
        self.assertTrue(validate_config_spec_hash(spec))

        # Same but with s3 instead of s3h
        spec = get_sample_config_spec('somebucket', 'someprofile', 'someregion')
        spec[STORAGE_KEY][S3] = spec[STORAGE_KEY].pop(S3H)
        self.assertTrue(validate_config_spec_hash(spec))

        # None or empty cases
        self.assertFalse(validate_config_spec_hash(None))
        self.assertFalse(validate_config_spec_hash({}))

        # Missing elements
        spec = get_sample_config_spec('somebucket', 'someprofile', 'someregion')
        spec[STORAGE_KEY].pop(S3H)
        self.assertFalse(validate_config_spec_hash(spec))
        spec = get_sample_config_spec('somebucket', 'someprofile', 'someregion')
        spec.pop(STORAGE_KEY)
        self.assertFalse(validate_config_spec_hash(spec))

    def test_validate_dataset_spec_hash(self):
        # Success case
        spec = get_sample_spec('somebucket')
        self.assertTrue(validate_spec_hash(spec))

        # None or empty cases
        self.assertFalse(validate_spec_hash(None))
        self.assertFalse(validate_spec_hash({}))

        # Non-integer version
        spec[DATASETS]['version'] = 'string'
        self.assertFalse(validate_spec_hash(spec))

        # Missing version
        spec[DATASETS].pop('version')
        self.assertFalse(validate_spec_hash(spec))

        # Missing dataset
        spec.pop(DATASETS)
        self.assertFalse(validate_spec_hash(spec))

        # Empty category list
        spec = get_sample_spec('somebucket')
        spec[DATASETS]['categories'] = {}
        self.assertFalse(validate_spec_hash(spec))

        # Missing categories
        spec[DATASETS].pop('categories')
        self.assertFalse(validate_spec_hash(spec))

        # Missing storage
        spec = get_sample_spec('somebucket')
        spec[DATASETS]['manifest'].pop(STORAGE_KEY)
        self.assertFalse(validate_spec_hash(spec))

        # Missing manifest
        spec[DATASETS].pop('manifest')

        # Bad bucket URL format
        spec = get_sample_spec('somebucket')
        spec[DATASETS]['manifest'][STORAGE_KEY] = 'invalid'
        self.assertFalse(validate_spec_hash(spec))

        # Missing and empty dataset name
        spec = get_sample_spec('somebucket')
        spec[DATASETS]['name'] = ''
        self.assertFalse(validate_spec_hash(spec))
        spec[DATASETS].pop('name')
        self.assertFalse(validate_spec_hash(spec))

    def test_config_verbose(self):
        self.assertFalse(config_verbose() is None)

    def test_config_load(self):
        mlgit_config_load()

    @pytest.mark.usefixtures('switch_to_test_dir')
    def test_paths(self):
        config = config_load()
        self.assertTrue(len(get_index_path(config)) > 0)
        self.assertTrue(len(get_objects_path(config)) > 0)
        self.assertTrue(len(get_cache_path(config)) > 0)
        self.assertTrue(len(get_metadata_path(config)) > 0)
        self.assertTrue('.ml-git' in get_refs_path(config))

    def test_list_repos(self):
        self.assertTrue(list_repos() is None)

    @pytest.mark.usefixtures('switch_to_test_dir')
    def test_import_dir(self):
        root_path = get_root_path()
        src = os.path.join(root_path, 'hdata')
        dst = os.path.join(root_path, 'dst_dir')
        import_dir(src, dst)
        self.assertTrue(len(os.listdir(dst)) > 0)
        self.assertTrue(len(os.listdir(src)) > 0)
        shutil.rmtree(dst)

    def test_extract_storage_info_from_list(self):
        array = [S3H, 'fakestorage']
        self.assertEqual(extract_storage_info_from_list(array), (S3H, 'fakestorage'))

    @pytest.mark.usefixtures('switch_to_test_dir')
    def test_create_workspace_tree_structure(self):
        root_path = get_root_path()
        IMPORT_PATH = os.path.join(os.getcwd(), 'test', 'src')
        os.makedirs(IMPORT_PATH)
        self.assertTrue(create_workspace_tree_structure('repotype', 'artefact_name',
                                                        ['imgs', 'old', 'blue'], S3H, 'minio', 2, IMPORT_PATH, Mutability.STRICT.value))

        spec_path = os.path.join(os.getcwd(), os.sep.join(['repotype', 'artefact_name', 'artefact_name.spec']))
        spec1 = yaml_load(spec_path)
        self.assertEqual(spec1['repotype']['manifest'][STORAGE_KEY], 's3h://minio')
        self.assertEqual(spec1['repotype']['name'], 'artefact_name')
        self.assertEqual(spec1['repotype']['mutability'], STRICT)
        self.assertEqual(spec1['repotype']['version'], 2)

        shutil.rmtree(IMPORT_PATH)
        shutil.rmtree(os.path.join(root_path, 'repotype'))

    @pytest.mark.usefixtures('restore_config')
    def test_get_batch_size(self):
        config = config_load()
        batch_size = get_batch_size(config)
        self.assertEqual(batch_size, BATCH_SIZE_VALUE)
        config[BATCH_SIZE] = 0
        self.assertRaises(Exception, lambda: get_batch_size(config))
        config[BATCH_SIZE] = 'string'
        self.assertRaises(Exception, lambda: get_batch_size(config))
        del config[BATCH_SIZE]
        batch_size = get_batch_size(config)
        self.assertEqual(batch_size, BATCH_SIZE_VALUE)

    def test_merge_conf(self):
        local_conf = {DATASETS: {'git': ''}}
        global_conf = {DATASETS: {'git': 'url'}, MODELS: {'git': 'url'}, STORAGE_KEY: {}}
        merge_conf(local_conf, global_conf)
        self.assertEqual(local_conf[DATASETS]['git'], 'url')
        self.assertEqual(local_conf[EntityType.MODELS.value]['git'], 'url')
        self.assertTrue(STORAGE_KEY in local_conf)

    @pytest.mark.usefixtures('restore_config')
    def test_merge_local_with_global_config(self):
        global_conf = {DATASETS: {'git': 'url'}, MODELS: {'git': 'url'}, STORAGE_KEY: {}}

        with mock.patch('ml_git.config.global_config_load', return_value=global_conf):
            merge_local_with_global_config()

        self.assertEqual(mlgit_config[DATASETS]['git'], 'url')
        self.assertEqual(mlgit_config[EntityType.MODELS.value]['git'], 'url')
        self.assertNotEqual(mlgit_config[STORAGE_KEY], {})

    @pytest.mark.usefixtures('restore_config', 'switch_to_tmp_dir')
    def test_save_global_config_in_local(self):
        remote_default = 'git_local_server.git'
        new_remote = 'git_local_server2.git'
        init_mlgit()
        self.assertTrue(os.path.isdir('.ml-git'))
        config = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config[DATASETS]['git'], remote_default)
        global_conf = {DATASETS: {'git': 'url'}, MODELS: {'git': 'url'}, EntityType.LABELS.value: {'git': new_remote}, STORAGE_KEY: {}}

        with mock.patch('ml_git.config.global_config_load', return_value=global_conf):
            save_global_config_in_local()

        config = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config[LABELS]['git'], new_remote)

    @pytest.mark.usefixtures('switch_to_test_dir')
    def test_start_wizard_questions(self):

        new_s3_storage_options = ['git_repo', 'endpoint', 'default', 'mlgit', S3H, 'X']
        invalid_storage_options = ['invalid_storage', 'X']
        new_gdrive_storage_options = ['git_repo', '.credentials', 'mlgit', GDRIVEH, 'X']

        with mock.patch('builtins.input', return_value='1'):
            has_new_storage, storage_type, bucket, profile, endpoint_url, git_repo = start_wizard_questions(DATASETS)
            self.assertEqual(storage_type, S3)
            self.assertEqual(bucket, 'mlgit-datasets')
            self.assertIsNone(profile)
            self.assertIsNone(endpoint_url)
            self.assertEqual(git_repo, 'git_local_server.git')
            self.assertFalse(has_new_storage)

        with mock.patch('builtins.input', new=lambda *args, **kwargs: invalid_storage_options.pop()):
            self.assertRaises(Exception, lambda: start_wizard_questions(DATASETS))

        with mock.patch('builtins.input', new=lambda *args, **kwargs: new_s3_storage_options.pop()):
            has_new_storage, storage_type, bucket, profile, endpoint_url, git_repo = start_wizard_questions(DATASETS)
            self.assertEqual(storage_type, S3H)
            self.assertEqual(bucket, 'mlgit')
            self.assertEqual(profile, 'default')
            self.assertEqual(endpoint_url, 'endpoint')
            self.assertEqual(git_repo, 'git_repo')
            self.assertTrue(has_new_storage)

        with mock.patch('builtins.input', new=lambda *args, **kwargs: new_gdrive_storage_options.pop()):
            has_new_storage, storage_type, bucket, profile, endpoint_url, git_repo = start_wizard_questions(DATASETS)
            self.assertEqual(storage_type, GDRIVEH)
            self.assertEqual(bucket, 'mlgit')
            self.assertEqual(profile, '.credentials')
            self.assertIsNone(endpoint_url)
            self.assertEqual(git_repo, 'git_repo')
            self.assertTrue(has_new_storage)
