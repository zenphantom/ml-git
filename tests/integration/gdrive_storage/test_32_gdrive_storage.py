"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.constants import Mutability
from tests.integration.commands import MLGIT_IMPORT, MLGIT_CREATE, MLGIT_INIT
from tests.integration.helper import ML_GIT_DIR, CREDENTIALS_PATH, ERROR_MESSAGE, DATASETS, DATASET_NAME
from tests.integration.helper import check_output, clear, init_repository, add_file
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir', 'google_drive_links')
class GdrivePushFilesAcceptanceTests(unittest.TestCase):

    @pytest.mark.usefixtures('switch_to_tmp_dir_with_gdrive_credentials', 'start_local_git_server')
    def test_01_push_and_checkout(self):
        cpath = 'credentials-json'
        init_repository(DATASETS, self, storage_type='gdriveh', profile=cpath)
        add_file(self, DATASETS, '--bumpversion', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata')
        self.assertIn(messages[17] % (metadata_path, DATASET_NAME),
                      check_output('ml-git datasets commit datasets-ex'))

        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs', DATASET_NAME, 'HEAD')

        self.assertTrue(os.path.exists(HEAD))
        self.assertNotIn(ERROR_MESSAGE, check_output('ml-git datasets push datasets-ex'))
        os.chdir(metadata_path)

        tag = 'computer-vision__images__datasets-ex__2'
        self.assertIn(tag, check_output('git describe --tags'))

        os.chdir(self.tmp_dir)

        workspace = os.path.join(self.tmp_dir, DATASETS)
        clear(workspace)
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR))
        init_repository(DATASETS, self, storage_type='gdriveh', profile=cpath)

        self.assertNotIn(ERROR_MESSAGE, check_output('ml-git datasets checkout %s' % tag))

        objects = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'objects')
        refs = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'cache')
        spec_file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'datasets-ex.spec')
        file = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME, 'newfile0')

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(file))
        self.assertTrue(os.path.exists(spec_file))

    @pytest.mark.usefixtures('switch_to_tmp_dir_with_gdrive_credentials', 'start_local_git_server')
    def test_02_import_with_gdrive(self):
        cpath = 'credentials-json'
        init_repository(DATASETS, self)

        file_path_b = os.path.join(DATASET_NAME, 'B')
        self.assertNotIn(ERROR_MESSAGE, check_output(
            MLGIT_IMPORT % (DATASETS, 'mlgit', DATASET_NAME) + ' --storage-type=gdrive --object=B --credentials=' + CREDENTIALS_PATH))

        self.assertTrue(os.path.exists(file_path_b))

        file_path = os.path.join(DATASET_NAME, 'test-folder', 'A')

        self.assertNotIn(ERROR_MESSAGE, check_output(
            MLGIT_IMPORT % (DATASETS, 'mlgit', DATASET_NAME) + ' --storage-type=gdrive --path=test-folder --credentials=' + cpath))

        self.assertTrue(os.path.exists(file_path))

    @pytest.mark.usefixtures('switch_to_tmp_dir_with_gdrive_credentials', 'start_local_git_server')
    def test_03_create_gdrive(self):
        self.assertIn(messages[0], check_output(MLGIT_INIT))

        self.assertIn(messages[38], check_output(MLGIT_CREATE % (DATASETS, DATASET_NAME)
                                                 + ' --category=imgs --bucket-name=test'
                                                   ' --import-url=%s --credentials-path=%s '
                                                 % (self.gdrive_links['test-folder'], CREDENTIALS_PATH)
                                                 + ' --mutability=%s' % Mutability.STRICT.value))

        file_a_test_folder = os.path.join(DATASETS, DATASET_NAME, 'data', 'test-folder', 'A')

        self.assertTrue(os.path.exists(file_a_test_folder))

        self.assertIn(messages[38], check_output(MLGIT_CREATE % (DATASETS, 'datasets-ex2')
                                                 + ' --category=imgs --bucket-name=test'
                                                   ' --import-url=%s --credentials-path=%s'
                                                 % (self.gdrive_links['B'], CREDENTIALS_PATH)
                                                 + ' --mutability=%s' % Mutability.STRICT.value))

        file_b = os.path.join(DATASETS, 'datasets-ex2', 'data', 'B')

        self.assertTrue(os.path.exists(file_b))


    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_04_create_with_wrong_import_url(self):
        entity_type = DATASETS
        self.assertIn(messages[0], check_output(MLGIT_INIT))
        self.assertIn(messages[91] % 'import_url', check_output(MLGIT_CREATE % (entity_type, entity_type + '-ex')
                                                                + ' --category=img --version=1 --import-url="import_url" '
                                                                  '--credentials-path=test' + ' --mutability=' + Mutability.STRICT.value))
