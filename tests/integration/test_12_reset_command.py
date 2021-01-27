"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from ml_git.utils import ensure_path_exists
from tests.integration.commands import MLGIT_ADD, MLGIT_COMMIT, MLGIT_RESET, MLGIT_STATUS
from tests.integration.helper import ML_GIT_DIR, DATASETS, DATASET_NAME
from tests.integration.helper import check_output, init_repository, ERROR_MESSAGE, create_file
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class ResetAcceptanceTests(unittest.TestCase):
    dataset_tag = 'computer-vision__images__datasets-ex__2'

    def set_up_reset(self):
        init_repository(DATASETS, self)
        create_file(os.path.join(DATASETS, DATASET_NAME), 'file1', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'),
                                      os.path.join('computer-vision', 'images', DATASET_NAME)),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))
        create_file(os.path.join(DATASETS, DATASET_NAME), 'file2', '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion')))
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'metadata'),
                                      os.path.join('computer-vision', 'images', DATASET_NAME)),
                      check_output(MLGIT_COMMIT % (DATASETS, DATASET_NAME, '')))

    def _check_dir(self, tag):
        os.chdir(os.path.join(ML_GIT_DIR, DATASETS, 'metadata'))
        self.assertIn(tag, check_output('git describe --tags'))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_soft_with_HEAD1(self):
        self.set_up_reset()
        self.assertIn(output_messages['INFO_INITIALIZING_RESET'] % ('--soft', 'HEAD~1'),
                      check_output(MLGIT_RESET % (DATASETS, DATASET_NAME) + ' --soft --reference=head~1'))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Changes to be committed:\n\tNew file: datasets-ex.spec\n\tNew file: file2\n\nUntracked files:\n\nCorrupted files:')

        self._check_dir(self.dataset_tag)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_mixed_with_HEAD1(self):
        self.set_up_reset()
        self.assertIn(output_messages['INFO_INITIALIZING_RESET'] % ('--mixed', 'HEAD~1'),
                      check_output(MLGIT_RESET % (DATASETS, DATASET_NAME) + ' --mixed --reference=head~1'))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Changes to be committed:\n\tNew file: datasets-ex.spec\n\nUntracked files:\n\tfile2\n\nCorrupted files:')
        self._check_dir(self.dataset_tag)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_hard_with_HEAD(self):
        self.set_up_reset()
        create_file(os.path.join(DATASETS, DATASET_NAME), 'file3', '0', '')
        check_output(MLGIT_ADD % (DATASETS, DATASET_NAME, '--bumpversion'))
        self.assertIn(output_messages['INFO_INITIALIZING_RESET'] % ('--hard', 'HEAD'),
                      check_output(MLGIT_RESET % (DATASETS, DATASET_NAME) + ' --hard --reference=head'))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Changes to be committed:\n\tNew file: datasets-ex.spec\n\nUntracked files:\n\nCorrupted files:')
        self._check_dir('computer-vision__images__datasets-ex__3')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_hard_with_HEAD1(self):
        self.set_up_reset()
        self.assertIn(output_messages['INFO_INITIALIZING_RESET'] % ('--hard', 'HEAD~1'),
                      check_output(MLGIT_RESET % (DATASETS, DATASET_NAME) + ' --hard --reference=head~1'))
        self.assertRegex(check_output(MLGIT_STATUS % (DATASETS, DATASET_NAME)),
                         r'Changes to be committed:\n\tNew file: datasets-ex.spec\n\nUntracked files:\n\nCorrupted files')
        self._check_dir(self.dataset_tag)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_hard_with_data_in_subpath(self):
        entity = DATASETS
        subpath = 'data'

        init_repository(entity, self)
        first_commit_file_name = 'file1'
        data_path = os.path.join(entity, entity+'-ex', subpath)
        ensure_path_exists(data_path)
        create_file(data_path, first_commit_file_name, '0', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity, entity+'-ex', '--bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity+'-ex', '')))

        second_commit_file_name = 'file2'
        create_file(data_path, second_commit_file_name, '1', '')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity, entity+'-ex', '--bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity+'-ex', '')))

        self.assertTrue(os.path.exists(os.path.join(data_path, first_commit_file_name)))
        self.assertTrue(os.path.exists(os.path.join(data_path, second_commit_file_name)))
        self.assertIn(output_messages['INFO_INITIALIZING_RESET'] % ('--hard', 'HEAD~1'),
                      check_output(MLGIT_RESET % (entity, entity+'-ex') + ' --hard --reference=head~1'))
        self.assertTrue(os.path.exists(os.path.join(data_path, first_commit_file_name)))
        self.assertFalse(os.path.exists(os.path.join(data_path, second_commit_file_name)))
        self.assertRegex(check_output(MLGIT_STATUS % (entity, entity+'-ex')),
                         r'Changes to be committed:\n\tNew file: datasets-ex.spec\n\nUntracked files:\n\nCorrupted files')
        self._check_dir(self.dataset_tag)
