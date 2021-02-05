"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest
from prettytable import PrettyTable

from tests.integration.commands import MLGIT_ADD, MLGIT_COMMIT, MLGIT_LOG
from tests.integration.helper import ML_GIT_DIR, add_file, create_spec, delete_file, ERROR_MESSAGE
from tests.integration.helper import check_output, init_repository
from tests.integration.output_messages import messages


@pytest.mark.usefixtures('tmp_dir')
class LogTests(unittest.TestCase):
    COMMIT_MESSAGE = 'test_message'
    TAG = 'computer-vision__images__dataset-ex__1'

    def set_up_test(self, repo_type='dataset', with_metrics=False):
        entity = '{}-ex'.format(repo_type)
        init_repository(repo_type, self)
        create_spec(self, repo_type, self.tmp_dir)
        metrics_options = ''
        if with_metrics:
            metrics_options = '--metric Accuracy 1 --metric Recall 2'
        self.assertIn(messages[13] % repo_type, check_output(MLGIT_ADD % (repo_type, entity, metrics_options)))
        self.assertIn(messages[17] % (os.path.join(self.tmp_dir, ML_GIT_DIR, repo_type, 'metadata'), entity),
                      check_output(MLGIT_COMMIT % (repo_type, entity, '-m ' + self.COMMIT_MESSAGE)))

    @staticmethod
    def create_metrics_table():
        test_table = PrettyTable()
        test_table.field_names = ['Name', 'Value']
        test_table.align['Name'] = 'l'
        test_table.align['Value'] = 'l'
        test_table.add_row(['Accuracy', 1.0])
        test_table.add_row(['Recall', 2.0])
        test_metrics = '\nmetrics:\n{}'.format(test_table.get_string())
        return test_metrics

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_log(self):
        self.set_up_test()
        output = check_output(MLGIT_LOG % ('dataset', 'dataset-ex', ''))
        self.assertIn(messages[77] % self.TAG, output)
        self.assertIn(messages[78] % self.COMMIT_MESSAGE, output)
        self.assertNotIn(messages[79] % 0, output)
        self.assertNotIn(messages[80] % 0, output)
        self.assertNotIn(messages[81], output)
        self.assertNotIn(messages[82], output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_log_with_stat(self):
        self.set_up_test()
        output = check_output(MLGIT_LOG % ('dataset', 'dataset-ex', '--stat'))
        self.assertIn(messages[79] % 0, output)
        self.assertIn(messages[80] % 0, output)
        self.assertNotIn(messages[81] % 0, output)
        self.assertNotIn(messages[82] % 0, output)
        self.assertNotIn(messages[83] % 0, output)
        self.assertNotIn(messages[84] % 0, output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_log_with_fullstat(self):
        self.set_up_test()
        add_file(self, 'dataset', '--bumpversion')
        check_output(MLGIT_COMMIT % ('dataset', 'dataset-ex', ''))
        amount_files = 5
        workspace_size = 14

        output = check_output(MLGIT_LOG % ('dataset', 'dataset-ex', '--fullstat'))

        files = ['newfile4', 'file2', 'file0', 'file3']

        for file in files:
            self.assertIn(file, output)

        self.assertIn(messages[84] % amount_files, output)
        self.assertIn(messages[83] % workspace_size, output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_log_with_fullstat_files_added_and_deleted(self):
        self.set_up_test()
        add_file(self, 'dataset', '--bumpversion')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % ('dataset', 'dataset-ex', '')))
        added = 4
        deleted = 1
        workspace_path = os.path.join(self.tmp_dir, 'dataset', 'dataset-ex')
        files = ['file2', 'newfile4']
        delete_file(workspace_path, files)
        add_file(self, 'dataset', '--bumpversion', 'img')
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % ('dataset', 'dataset-ex', '')))
        output = check_output(MLGIT_LOG % ('dataset', 'dataset-ex', '--fullstat'))
        self.assertIn(messages[81] % added, output)
        self.assertIn(messages[82] % deleted, output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_log_metrics(self):
        repo_type = 'model'
        entity = '{}-ex'.format(repo_type)
        self.set_up_test(repo_type, with_metrics=True)
        output = check_output(MLGIT_LOG % (repo_type, entity, ''))
        self.assertIn(messages[77] % self.TAG.replace('dataset-ex', entity), output)
        self.assertIn(messages[78] % self.COMMIT_MESSAGE, output)
        self.assertNotIn(messages[79] % 0, output)
        self.assertNotIn(messages[80] % 0, output)
        self.assertNotIn(messages[81], output)
        self.assertNotIn(messages[82], output)
        self.assertIn(self.create_metrics_table(), output)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_log_metrics_wrong_entity(self):
        repo_type = 'labels'
        entity = '{}-ex'.format(repo_type)
        self.set_up_test(repo_type, with_metrics=True)
        output = check_output(MLGIT_LOG % (repo_type, entity, ''))
        self.assertIn(messages[77] % self.TAG.replace('dataset-ex', entity), output)
        self.assertIn(messages[78] % self.COMMIT_MESSAGE, output)
        self.assertNotIn(messages[79] % 0, output)
        self.assertNotIn(messages[80] % 0, output)
        self.assertNotIn(messages[81], output)
        self.assertNotIn(messages[82], output)
        self.assertNotIn(self.create_metrics_table(), output)
