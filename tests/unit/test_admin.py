"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import io
import os
import unittest
from contextlib import redirect_stdout
from unittest import mock

import pytest

from ml_git.admin import init_mlgit, remote_add, storage_add, clone_config_repository, storage_del, remote_del
from ml_git.constants import STORAGE_CONFIG_KEY
from ml_git.utils import yaml_load
from tests.unit.conftest import AZUREBLOBH, DATASETS, S3


@pytest.mark.usefixtures('tmp_dir')
class AdminTestCases(unittest.TestCase):

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_mlgit_init(self):
        init_mlgit()
        self.assertTrue(os.path.isdir('.ml-git'))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_mlgit_init_without_permission(self):
        output = io.StringIO()
        with mock.patch('os.mkdir', side_effect=PermissionError()):
            with redirect_stdout(output):
                init_mlgit()

        self.assertIn('Permission denied.', output.getvalue())

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_remote_add(self):
        remote_default = 'git_local_server.git'
        new_remote = 'git_local_server2.git'
        init_mlgit()
        remote_add(DATASETS, new_remote)
        self.assertTrue(os.path.isdir('.ml-git'))
        config = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config[DATASETS]['git'], new_remote)
        self.assertNotEqual(remote_default, new_remote)
        remote_add(DATASETS, '')
        config_ = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config_[DATASETS]['git'], '')
        remote_add(DATASETS, new_remote)
        self.assertTrue(os.path.isdir('.ml-git'))
        config__ = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config__[DATASETS]['git'], new_remote)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_storage_add(self):
        init_mlgit()
        storage_add(S3, 'bucket_test', 'personal')
        config_edit = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config_edit[STORAGE_CONFIG_KEY][S3]['bucket_test']['aws-credentials']['profile'], 'personal')
        self.assertEqual(config_edit[STORAGE_CONFIG_KEY][S3]['bucket_test']['region'], None)
        s = storage_add('s4', 'bucket_test', 'personal')
        self.assertEqual(s, None)
        config = yaml_load('.ml-git/config.yaml')
        self.assertTrue(S3 in config[STORAGE_CONFIG_KEY])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_storage_del(self):
        init_mlgit()
        storage_add(S3, 'bucket_test', 'personal')
        config_edit = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config_edit[STORAGE_CONFIG_KEY][S3]['bucket_test']['aws-credentials']['profile'], 'personal')
        storage_del(S3, 'bucket_test')
        config = yaml_load('.ml-git/config.yaml')
        self.assertFalse(S3 in config[STORAGE_CONFIG_KEY] and 'bucket_test' in config[STORAGE_CONFIG_KEY][S3])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_storage_add_check_type_azureblobh(self):
        init_mlgit()
        storage_type = AZUREBLOBH
        container = 'azure'
        self.check_storage(container, storage_type, self.tmp_dir)

    def check_storage(self, container, storage_type, tmpdir):
        storage_add(storage_type, container, 'personal')
        config_edit = yaml_load(os.path.join(tmpdir, '.ml-git/config.yaml'))
        self.assertIn(storage_type, config_edit[STORAGE_CONFIG_KEY])
        self.assertIn(container, config_edit[STORAGE_CONFIG_KEY][storage_type])

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_clone_local_git_server')
    def test_clone_config_repository(self):
        folder_name = 'test'
        self.assertTrue(clone_config_repository(os.path.join(self.tmp_dir, 'git_local_server.git'), folder_name, False))

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_remote_add_global_config(self):
        remote_default = 'git_local_server.git'
        new_remote = 'git_local_server2.git'
        init_mlgit()
        with mock.patch('pathlib.Path.home', return_value=self.tmp_dir):
            remote_add(DATASETS, new_remote, global_conf=True)

        self.assertTrue(os.path.exists('.mlgitconfig'))
        config = yaml_load('.ml-git/config.yaml')
        config_global = yaml_load('.mlgitconfig')
        self.assertEqual(config_global[DATASETS]['git'], new_remote)
        self.assertNotEqual(config[DATASETS]['git'], remote_default)

        with mock.patch('pathlib.Path.home', return_value=self.tmp_dir):
            remote_add(DATASETS, '', global_conf=True)

        config_ = yaml_load('.mlgitconfig')
        self.assertEqual(config_[DATASETS]['git'], '')

        with mock.patch('pathlib.Path.home', return_value=self.tmp_dir):
            remote_add(DATASETS, new_remote, global_conf=True)

        config__ = yaml_load('.mlgitconfig')
        self.assertEqual(config__[DATASETS]['git'], new_remote)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_storage_add_global_config(self):
        init_mlgit()
        with mock.patch('pathlib.Path.home', return_value=self.tmp_dir):
            storage_add(S3, 'bucket_test', 'personal', global_conf=True)

        config_edit = yaml_load('.mlgitconfig')
        self.assertEqual(config_edit[STORAGE_CONFIG_KEY][S3]['bucket_test']['aws-credentials']['profile'], 'personal')
        self.assertEqual(config_edit[STORAGE_CONFIG_KEY][S3]['bucket_test']['region'], None)

        with mock.patch('pathlib.Path.home', return_value=self.tmp_dir):
            s = storage_add('s4', 'bucket_test', 'personal', global_conf=True)

        self.assertEqual(s, None)
        config = yaml_load('.mlgitconfig')
        self.assertTrue(S3 in config[STORAGE_CONFIG_KEY])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_storage_del_global_config(self):
        with mock.patch('pathlib.Path.home', return_value=self.tmp_dir):
            init_mlgit()
            storage_add(S3, 'bucket_test', 'personal', global_conf=True)

        config_edit = yaml_load('.mlgitconfig')
        self.assertEqual(config_edit[STORAGE_CONFIG_KEY][S3]['bucket_test']['aws-credentials']['profile'], 'personal')

        with mock.patch('pathlib.Path.home', return_value=self.tmp_dir):
            storage_del(S3, 'bucket_test', global_conf=True)

        config = yaml_load('.mlgitconfig')
        self.assertFalse(S3 in config[STORAGE_CONFIG_KEY] and 'bucket_test' in config[STORAGE_CONFIG_KEY][S3])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_storage_add_without_credentials(self):
        init_mlgit()
        storage_add(S3, 'bucket_test', None)
        config_edit = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config_edit[STORAGE_CONFIG_KEY][S3]['bucket_test']['aws-credentials']['profile'], None)
        self.assertEqual(config_edit[STORAGE_CONFIG_KEY][S3]['bucket_test']['region'], None)
        s = storage_add('s4', 'bucket_test', 'personal')
        self.assertEqual(s, None)
        config = yaml_load('.ml-git/config.yaml')
        self.assertTrue(S3 in config[STORAGE_CONFIG_KEY])

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_remote_del(self):
        remote_default = 'git_local_server.git'
        init_mlgit()
        config = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config[DATASETS]['git'], '')
        remote_add(DATASETS, remote_default)
        config = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config[DATASETS]['git'], remote_default)
        remote_del(DATASETS)
        config_ = yaml_load('.ml-git/config.yaml')
        self.assertEqual(config_[DATASETS]['git'], '')
