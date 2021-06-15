"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import os
import unittest

import pytest

from ml_git.constants import CONFIG_FILE
from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_INIT, MLGIT_CONFIG_SHOW, MLGIT_CLONE, MLGIT_CONFIG_PUSH, \
    MLGIT_CONFIG_REMOTE
from tests.integration.helper import check_output, CLONE_FOLDER, ERROR_MESSAGE, GIT_PATH, \
    create_git_clone_repo, PATH_TEST

GIT_LOG_COMMAND = 'git log --pretty=format:"%h - %an, %ar : %s"'


@pytest.mark.usefixtures('tmp_dir')
class ConfigAcceptanceTests(unittest.TestCase):
    threads_per_core = 5
    push_threads_count = os.cpu_count() * threads_per_core
    expected_result = "config:\n{'batch_size': 20,\n 'cache_path': '',\n 'datasets': {'git': ''}," \
                      "\n 'index_path': '',\n 'labels': {'git': ''},\n 'metadata_path': '',\n 'mlgit_conf': 'config.yaml'," \
                      "\n 'mlgit_path': '.ml-git',\n 'models': {'git': ''},\n 'object_path': ''," \
                      "\n 'push_threads_count': "+str(push_threads_count)+",\n 'refs_path': ''," \
                      "\n 'storages': {'s3': {'mlgit-datasets': {'aws-credentials': {'profile': 'default'}," \
                      "\n                                        'region': 'us-east-1'}}},\n 'verbose': 'info'}"

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_01_config_show_command(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(self.expected_result, check_output(MLGIT_CONFIG_SHOW))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_add_remote_config(self):
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_INIT))
        git_url = os.path.join(self.tmp_dir, GIT_PATH)
        self.assertFalse(os.path.exists('.git'))
        self.assertIn(output_messages['INFO_CREATING_REMOTE'] % git_url, check_output(MLGIT_CONFIG_REMOTE % git_url))
        self.assertTrue(os.path.exists('.git'))
        self.assertTrue(os.path.exists('.gitignore'))
        self.assertIn(GIT_PATH, check_output('git remote -v'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_add_remote_in_empty_folder(self):
        git_url = os.path.join(self.tmp_dir, GIT_PATH)
        self.assertFalse(os.path.exists('.git'))
        self.assertIn(output_messages['ERROR_NOT_IN_RESPOSITORY'], check_output(MLGIT_CONFIG_REMOTE % git_url))
        self.assertFalse(os.path.exists('.git'))
        self.assertNotIn(git_url, check_output('git remote -v'))

    @pytest.mark.usefixtures('start_empty_git_server', 'switch_to_tmp_dir')
    def test_04_config_push_after_remote_add(self):
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_INIT))
        git_url = os.path.join(self.tmp_dir, GIT_PATH)
        self.assertIn(output_messages['INFO_CREATING_REMOTE'] % git_url, check_output(MLGIT_CONFIG_REMOTE % git_url))
        self.assertTrue(os.path.exists('.git'))

        output = check_output(MLGIT_CONFIG_PUSH % '')
        config_file_path = os.path.join(self.tmp_dir, CONFIG_FILE)
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (self.tmp_dir, config_file_path), output)
        self.assertIn(output_messages['INFO_PUSH_CONFIG_FILE'], output)
        self.assertNotIn(ERROR_MESSAGE, output)
        self.assertIn('Updating config file', check_output(GIT_LOG_COMMAND))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_config_push_in_empty_folder(self):
        output = check_output(MLGIT_CONFIG_PUSH % '')
        config_file_path = os.path.join(self.tmp_dir, CONFIG_FILE)
        self.assertIn(output_messages['ERROR_NOT_IN_RESPOSITORY'], output)
        self.assertNotIn(output_messages['INFO_COMMIT_REPO'] % (self.tmp_dir, config_file_path), output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_config_push_after_clone(self):
        git_repository = os.path.join(PATH_TEST, 'git_clone.git')
        os.makedirs(git_repository, exist_ok=True)
        create_git_clone_repo(git_repository, self.tmp_dir)
        self.assertIn(output_messages['INFO_SUCCESS_LOAD_CONFIGURATION'], check_output(MLGIT_CLONE % (git_repository, '--folder=' + CLONE_FOLDER)))
        self.assertTrue(os.path.exists(os.path.join(CLONE_FOLDER, '.git')))
        self.assertTrue(os.path.exists(os.path.join(CLONE_FOLDER, '.gitignore')))

        os.chdir(CLONE_FOLDER)
        output = check_output(MLGIT_CONFIG_PUSH % '')
        config_file_path = os.path.join(self.tmp_dir, CLONE_FOLDER, CONFIG_FILE)
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, CLONE_FOLDER), config_file_path), output)
        self.assertIn(output_messages['INFO_PUSH_CONFIG_FILE'], output)
        self.assertNotIn(ERROR_MESSAGE, output)
        self.assertIn('Updating config file', check_output(GIT_LOG_COMMAND))

    @pytest.mark.usefixtures('start_empty_git_server', 'switch_to_tmp_dir')
    def test_07_config_push_with_message(self):
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_INIT))
        git_url = os.path.join(self.tmp_dir, GIT_PATH)
        self.assertIn(output_messages['INFO_CREATING_REMOTE'] % git_url, check_output(MLGIT_CONFIG_REMOTE % git_url))
        self.assertTrue(os.path.exists('.git'))
        self.assertTrue(os.path.exists('.gitignore'))

        message = 'My testing message'
        output = check_output(MLGIT_CONFIG_PUSH % '-m \"%s\"' % message)
        config_file_path = os.path.join(self.tmp_dir, CONFIG_FILE)
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (self.tmp_dir, config_file_path), output)
        self.assertIn(output_messages['INFO_PUSH_CONFIG_FILE'], output)
        self.assertNotIn(ERROR_MESSAGE, output)
        self.assertIn(message, check_output(GIT_LOG_COMMAND))
