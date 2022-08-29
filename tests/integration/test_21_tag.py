"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH, MLGIT_TAG_ADD
from tests.integration.helper import ML_GIT_DIR, create_file, ERROR_MESSAGE, DATASETS, DATASET_NAME
from tests.integration.helper import check_output, init_repository, add_file


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class TagAcceptanceTests(unittest.TestCase):

    def set_up_tag(self, entity_type):
        init_repository(entity_type, self)

    def _add_tag_entity(self, entity_type):
        self.set_up_tag(entity_type)

        add_file(self, entity_type, '--bumpversion', 'new')

        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, entity_type, 'metadata'), entity_type+'-ex'),
                      check_output(MLGIT_COMMIT % (entity_type, entity_type+'-ex', '')))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+'-ex')))

        with open(os.path.join(entity_type, entity_type + '-ex', 'file1'), 'wb') as z:
            z.write(b'0' * 1024)

        self.assertIn(output_messages['INFO_CREATE_TAG_SUCCESS'], check_output(MLGIT_TAG_ADD % (entity_type, entity_type+'-ex', 'test-tag')))

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity_type, entity_type+'-ex')))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_01_add_tag(self):
        self._add_tag_entity(DATASETS)

        tag_file = os.path.join(self.tmp_dir, 'local_git_server.git', 'refs', 'tags', 'test-tag')
        self.assertTrue(os.path.exists(tag_file))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_02_add_tag_wrong_entity(self):
        self.set_up_tag(DATASETS)

        self.assertIn(output_messages['ERROR_NO_CURRENT_TAG_FOR'] % 'dataset-wrong',
                      check_output(MLGIT_TAG_ADD % (DATASETS, 'dataset-wrong', 'test-tag')))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_03_add_tag_without_previous_commit(self):
        self.set_up_tag(DATASETS)

        self.assertIn(output_messages['ERROR_NO_CURRENT_TAG_FOR'] % DATASET_NAME, check_output(MLGIT_TAG_ADD % (DATASETS, DATASET_NAME, 'test-tag')))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_04_add_existing_tag(self):
        self._add_tag_entity(DATASETS)

        create_file(os.path.join(DATASETS, DATASET_NAME), 'file2', '0', '')

        tag_file = os.path.join(self.tmp_dir, 'local_git_server.git', 'refs', 'tags', 'test-tag')
        self.assertTrue(os.path.exists(tag_file))

        self.assertIn(output_messages['INFO_TAG_ALREDY_EXISTS'] % 'test-tag', check_output(MLGIT_TAG_ADD % (DATASETS, DATASET_NAME, 'test-tag')))
