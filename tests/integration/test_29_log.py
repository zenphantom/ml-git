"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from tests.integration.commands import MLGIT_ADD, MLGIT_COMMIT, MLGIT_LOG
from tests.integration.helper import ML_GIT_DIR, add_file, create_spec, delete_file, ERROR_MESSAGE, DATASETS, \
    DATASET_NAME, DATASET_TAG
from tests.integration.helper import check_output, init_repository
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class LogTests(unittest.TestCase):
    COMMIT_MESSAGE = 'test_message'

    def setUp_test(self):
        init_repository(DATASETS, self)
        create_spec(self, DATASETS, self.tmp_dir)
        self.assertIn(messages[13] % DATASETS, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '')))
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'),
                                      os.path.join('computer-vision', 'images', DATASET_NAME)),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '-m ' + self.COMMIT_MESSAGE)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_log(self):
        self.setUp_test()
        output = check_output(MLGIT_LOG % (DATASETS, DATASET_NAME, ''))
        self.assertIn(messages[77] % DATASET_TAG, output)
        self.assertIn(messages[78] % self.COMMIT_MESSAGE, output)
        self.assertNotIn(messages[79] % 0, output)
        self.assertNotIn(messages[80] % 0, output)
        self.assertNotIn(messages[81], output)
        self.assertNotIn(messages[82], output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_log_with_stat(self):
        self.setUp_test()
        output = check_output(MLGIT_LOG % (DATASETS, DATASET_NAME, '--stat'))
        self.assertIn(messages[79] % 0, output)
        self.assertIn(messages[80] % 0, output)
        self.assertNotIn(messages[81] % 0, output)
        self.assertNotIn(messages[82] % 0, output)
        self.assertNotIn(messages[83] % 0, output)
        self.assertNotIn(messages[84] % 0, output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_log_with_fullstat(self):
        self.setUp_test()
        add_file(self, DATASETS, '--bumpversion')
        check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, ''))
        amount_files = 5
        workspace_size = 14

        output = check_output(MLGIT_LOG % (DATASETS, DATASET_NAME, '--fullstat'))

        files = ['newfile4', 'file2', 'file0', 'file3']

        for file in files:
            self.assertIn(file, output)

        self.assertIn(messages[84] % amount_files, output)
        self.assertIn(messages[83] % workspace_size, output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_log_with_fullstat_files_added_and_deleted(self):
        self.setUp_test()
        add_file(self, DATASETS, '--bumpversion')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        added = 4
        deleted = 1
        workspace_path = os.path.join(self.tmp_dir, DATASETS, DATASET_NAME)
        files = ['file2', 'newfile4']
        delete_file(workspace_path, files)
        add_file(self, DATASETS, '--bumpversion', 'img')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        output = check_output(MLGIT_LOG % (DATASETS, DATASET_NAME, '--fullstat'))
        self.assertIn(messages[81] % added, output)
        self.assertIn(messages[82] % deleted, output)
