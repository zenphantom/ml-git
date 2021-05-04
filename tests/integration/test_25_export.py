"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_COMMIT, MLGIT_PUSH, MLGIT_EXPORT
from tests.integration.helper import ML_GIT_DIR, PROFILE, BUCKET_NAME, \
    check_output, init_repository, add_file, PATH_TEST, DATASETS, DATASET_NAME, MODELS, LABELS, S3H, S3


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class ExportTagAcceptanceTests(unittest.TestCase):

    def export(self, repotype, entity):
        init_repository(repotype, self)
        add_file(self, repotype, '', repotype)
        file_in_storage = os.path.join(PATH_TEST, 'data', 'mlgit', repotype+'file0')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (os.path.join(self.tmp_dir, ML_GIT_DIR, repotype, 'metadata'), entity),
                      check_output(MLGIT_COMMIT % (repotype, entity, '')))

        self.assertFalse(os.path.exists(file_in_storage))

        check_output(MLGIT_PUSH % (repotype, entity))
        storage = '%s://mlgit' % S3H
        tag = 'computer-vision__images__%s__1' % entity
        self.assertIn(output_messages['INFO_EXPORTING_TAG'] % (tag, storage, '%s://mlgit' % S3), check_output(MLGIT_EXPORT % (
            repotype, ' {} {} --credentials={} --endpoint=http://127.0.0.1:9000'.format(tag, BUCKET_NAME, PROFILE))))

        self.assertTrue(os.path.exists(file_in_storage))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_export_dataset_tag(self):

        self.export(DATASETS, DATASET_NAME)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_export_model_tag(self):

        self.export(MODELS, 'models-ex')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_export_labels_tag(self):
        self.export(LABELS, 'labels-ex')
