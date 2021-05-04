"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest
from unittest import mock

import pytest
from azure.storage.blob import BlobServiceClient, ContainerClient

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_INIT, MLGIT_REMOTE_ADD, MLGIT_ENTITY_INIT, MLGIT_COMMIT, MLGIT_PUSH, \
    MLGIT_CHECKOUT
from tests.integration.helper import ML_GIT_DIR, ERROR_MESSAGE, DATASETS, DATASET_NAME, DATASET_TAG, STRICT, AZUREBLOBH
from tests.integration.helper import check_output, clear, GIT_PATH, create_spec, add_file


@pytest.mark.usefixtures('tmp_dir', 'start_local_git_server', 'switch_to_tmp_dir')
class AzureAcceptanceTests(unittest.TestCase):
    repo_type = DATASETS
    storage_type = AZUREBLOBH
    bucket = 'mlgit'
    workspace = os.path.join(repo_type, repo_type + '-ex')
    dev_store_account_ = 'DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNO' \
                         'cqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobE' \
                         'ndpoint=http://127.0.0.1:10000/devstoreaccount1;'

    def set_up_push(self):
        os.makedirs(self.workspace)
        create_spec(self, self.repo_type, self.tmp_dir, version=1, mutability=STRICT, storage_type=self.storage_type)

        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (GIT_PATH, self.repo_type),
                      check_output(MLGIT_REMOTE_ADD % (self.repo_type, GIT_PATH)))
        self.assertIn(output_messages['INFO_ADD_STORAGE_WITHOUT_PROFILE'] % (self.storage_type, self.bucket),
                      check_output('ml-git repository storage add %s --type=%s' %
                                   (self.bucket, self.storage_type)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % DATASETS))

        add_file(self, self.repo_type, '', 'new')
        metadata_path = os.path.join(ML_GIT_DIR, DATASETS, 'metadata')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, metadata_path), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (self.repo_type, DATASET_NAME, '')))
        HEAD = os.path.join(ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(HEAD))

    def create_bucket(self, connection_string, container):
        client = BlobServiceClient.from_connection_string(connection_string)
        try:
            client.create_container(container)
            container = ContainerClient.from_connection_string(connection_string, container, connection_timeout=300)
            container.get_container_properties()
        except Exception:
            raise Exception(output_messages['ERROR_CANNOT_CREATE_AZURE_CONTAINER'])
        pass

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_create_azure_storage(self):
        self.create_bucket(self.dev_store_account_, self.bucket)
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (GIT_PATH, self.repo_type), check_output(MLGIT_REMOTE_ADD % (self.repo_type, GIT_PATH)))
        self.assertIn(output_messages['INFO_ADD_STORAGE_WITHOUT_PROFILE'] % (self.storage_type, self.bucket),
                      check_output('ml-git repository storage add %s --type=%s' %
                                   (self.bucket, self.storage_type)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % DATASETS))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'AZURE_STORAGE_CONNECTION_STRING': dev_store_account_})
    def test_02_push_file(self):
        self.set_up_push()
        self.assertEqual(os.getenv('AZURE_STORAGE_CONNECTION_STRING'), self.dev_store_account_)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (self.repo_type, DATASET_NAME)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'AZURE_STORAGE_CONNECTION_STRING': dev_store_account_})
    def test_03_checkout(self):
        os.makedirs(self.workspace)
        create_spec(self, self.repo_type, self.tmp_dir, version=1, mutability=STRICT, storage_type=self.storage_type)

        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(output_messages['INFO_ADD_REMOTE'] % (GIT_PATH, self.repo_type),
                      check_output(MLGIT_REMOTE_ADD % (self.repo_type, GIT_PATH)))
        self.assertIn(output_messages['INFO_ADD_STORAGE_WITHOUT_PROFILE'] % (self.storage_type, self.bucket),
                      check_output('ml-git repository storage add %s --type=%s' %
                                   (self.bucket, self.storage_type)))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % DATASETS))

        add_file(self, self.repo_type, '', 'new')
        metadata_path = os.path.join(ML_GIT_DIR, DATASETS, 'metadata')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] %
                      (os.path.join(self.tmp_dir, metadata_path), DATASET_NAME),
                      check_output(MLGIT_COMMIT % (self.repo_type, DATASET_NAME, '')))
        HEAD = os.path.join(ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')
        self.assertTrue(os.path.exists(HEAD))
        self.assertEqual(os.getenv('AZURE_STORAGE_CONNECTION_STRING'), self.dev_store_account_)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (self.repo_type, DATASET_NAME)))

        clear(self.workspace)
        clear(os.path.join(ML_GIT_DIR, DATASETS))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ENTITY_INIT % self.repo_type))
        self.assertEqual(os.getenv('AZURE_STORAGE_CONNECTION_STRING'), self.dev_store_account_)
        self.assertNotIn(ERROR_MESSAGE,
                         check_output(MLGIT_CHECKOUT % (self.repo_type, DATASET_TAG)))
        ws_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)

        self.assertTrue(os.path.isfile(os.path.join(ws_path, 'newfile0')))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, 'newfile1')))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, 'newfile2')))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, 'newfile3')))
        self.assertTrue(os.path.isfile(os.path.join(ws_path, 'newfile4')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_push_without_credentials(self):
        self.set_up_push()
        self.assertIn(output_messages['ERROR_AZURE_CREDENTIALS_NOT_FOUND'], check_output(MLGIT_PUSH % (self.repo_type, DATASET_NAME)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    @mock.patch.dict(os.environ, {'AZURE_STORAGE_CONNECTION_STRING': 'wrong_connection_string'})
    def test_05_push_with_wrong_connection_credential(self):
        self.set_up_push()
        self.assertIn(output_messages['INFO_UNABLE_AZURE_CONNECTION'], check_output(MLGIT_PUSH % (self.repo_type, DATASET_NAME)))
