"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil
import unittest
from pathlib import Path
from unittest import mock

import pytest

from ml_git.ml_git_message import output_messages
from ml_git.utils import ensure_path_exists
from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH
from tests.integration.helper import ML_GIT_DIR, MINIO_BUCKET_PATH, GIT_PATH
from tests.integration.helper import check_output, clear, init_repository, add_file, ERROR_MESSAGE
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class PushFilesAcceptanceTests(unittest.TestCase):

    def _push_entity(self, entity_type):
        clear(os.path.join(MINIO_BUCKET_PATH, 'zdj7WWjGAAJ8gdky5FKcVLfd63aiRUGb8fkc8We2bvsp9WW12'))
        init_repository(entity_type, self)
        add_file(self, entity_type, '--bumpversion', 'new', file_content='0')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')
        self.assertIn(messages[17] % (metadata_path, entity_type + '-ex'),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type + '-ex', '')))

        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'refs', entity_type+'-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+'-ex')))
        self.check_metadata_after_push(entity_type)

    def check_metadata_after_push(self, entity_type='dataset'):
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata')
        os.chdir(metadata_path)
        self.assertTrue(os.path.exists(
            os.path.join(MINIO_BUCKET_PATH, 'zdj7WWjGAAJ8gdky5FKcVLfd63aiRUGb8fkc8We2bvsp9WW12')))
        self.assertIn('computer-vision__images__' + entity_type + '-ex__2', check_output('git describe --tags'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_push_files_to_dataset(self):
        self._push_entity('dataset')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_push_files_to_labels(self):
        self._push_entity('labels')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_push_files_to_model(self):
        self._push_entity('model')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_push_with_wrong_repository(self):
        init_repository('dataset', self)
        add_file(self, 'dataset', '--bumpversion', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'metadata')
        self.assertIn(messages[17] % (metadata_path, 'dataset-ex'),
                      check_output(MLGIT_COMMIT % ('dataset',  'dataset-ex', '')))

        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, 'dataset', 'refs', 'dataset-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))

        git_path = os.path.join(self.tmp_dir, GIT_PATH)

        clear(git_path)

        output = check_output(MLGIT_PUSH % ('dataset', 'dataset-ex'))

        self.assertIn(ERROR_MESSAGE, output)
        self.assertIn(GIT_PATH, output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_push_with_wrong_credentials_profile(self):
        entity_type = 'dataset'
        artifact_name = 'dataset-ex'
        init_repository(entity_type, self, profile='personal2')
        add_file(self, entity_type, '--bumpversion', 'new')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity_type,  artifact_name, '')))
        self.assertIn(output_messages['ERROR_AWS_KEY_NOT_EXIST'], check_output(MLGIT_PUSH % (entity_type, artifact_name)))

    def set_up_push_without_profile(self, entity_type='dataset', artifact_name='dataset-ex'):
        init_repository(entity_type, self, profile=None)
        add_file(self, entity_type, '--bumpversion', 'new')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity_type, artifact_name, '')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'AWS_ACCESS_KEY_ID': 'fake_access_key'})
    @mock.patch.dict(os.environ, {'AWS_SECRET_ACCESS_KEY': 'fake_secret_key'})
    def test_06_push_with_environment_variables(self):
        entity_type = 'dataset'
        artifact_name = 'dataset-ex'
        self.set_up_push_without_profile()
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, artifact_name)))
        self.check_metadata_after_push(entity_type)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'AWS_SHARED_CREDENTIALS_FILE': os.path.join(Path('./tests/integration/.aws/credentials-default').resolve())})
    def test_07_push_with_default_aws_config(self):
        entity_type = 'dataset'
        artifact_name = 'dataset-ex'
        self.set_up_push_without_profile()
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, artifact_name)))
        self.check_metadata_after_push(entity_type)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_08_push_without_default_config(self):
        entity_type = 'dataset'
        artifact_name = 'dataset-ex'
        init_repository(entity_type, self, profile=None)
        add_file(self, entity_type, '--bumpversion', 'new')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity_type, artifact_name, '')))
        self.assertIn('Unable to locate credentials', check_output(MLGIT_PUSH % (entity_type, artifact_name)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_09_push_entity_with_dir(self):
        entity_type = 'dataset'
        artifact_name = 'dataset-ex'
        init_repository(entity_type, self)
        workspace = os.path.join(self.tmp_dir, entity_type, artifact_name)
        self.assertTrue(os.path.exists(workspace))
        entity_dir = os.path.join('folderA', 'folderB')
        workspace_with_dir = os.path.join(self.tmp_dir, entity_type, entity_dir)
        ensure_path_exists(workspace_with_dir)
        shutil.move(workspace, workspace_with_dir)
        add_file(self, entity_type, '--bumpversion', 'new', entity_dir=entity_dir)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity_type, artifact_name, '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, artifact_name)))
        self.assertTrue(os.path.exists(workspace_with_dir))
        self.assertTrue(os.path.exists(os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata', entity_dir)))
