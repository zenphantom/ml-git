"""
© Copyright 2020-2022 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_FETCH, MLGIT_PUSH, MLGIT_COMMIT
from tests.integration.helper import ML_GIT_DIR, ERROR_MESSAGE, add_file, GIT_PATH, MLGIT_ENTITY_INIT, check_output, \
    clear, init_repository, change_git_in_config, DATASETS, DATASET_TAG


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class FetchAcceptanceTests(unittest.TestCase):

    def set_up_fetch(self, entity=DATASETS):
        init_repository(entity, self)
        add_file(self, entity, '', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')
        workspace = os.path.join(self.tmp_dir, entity)
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, entity + '-ex'),
                      check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        HEAD = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'refs', entity + '-ex', 'HEAD')
        self.assertTrue(os.path.exists(HEAD))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity))
        clear(workspace)
        self.assertIn(output_messages['INFO_METADATA_INIT']
                      % (os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_01_fetch_metadata_specific_tag(self):
        self.set_up_fetch()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG)))

        hashfs = os.path.join(ML_GIT_DIR, DATASETS, 'objects', 'hashfs')

        self.assertTrue(os.path.exists(hashfs))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_02_fetch_with_group_sample(self):
        self.set_up_fetch()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG)
                                                     + ' --sample-type=group --sampling=1:3 --seed=4'))

        hashfs = os.path.join(ML_GIT_DIR, DATASETS, 'objects', 'hashfs')
        self.assertTrue(os.path.exists(hashfs))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_03_group_sample_with_amount_parameter_greater_than_frequency(self):
        self.set_up_fetch()

        self.assertIn(output_messages['ERROR_AMOUNT_PARAMETER_SHOULD_BE_SMALLER_GROUP_SIZE'],
                      check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG) + ' --sample-type=group --sampling=3:1 --seed=4'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_04_group_sample_with_seed_parameter_negative(self):
        self.set_up_fetch()

        self.assertIn(output_messages['ERROR_AMOUNT_GROUP_REQUIRES_POSITIVE'],
                      check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG) + ' --sample-type=group --sampling=1:2 --seed=-4'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_05_fetch_with_range_sample(self):
        self.set_up_fetch()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG)
                                                     + ' --sample-type=range --sampling=2:4:1'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_06_range_sample_with_start_parameter_greater_than_stop(self):
        self.set_up_fetch()

        self.assertIn(output_messages['ERROR_START_PARAMETER_SHOULD_BE_SMALLER_THAN_STOP'],
                      check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG) + ' --sample-type=range --sampling=4:2:1'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_07_range_sample_with_start_parameter_less_than_zero(self):
        self.set_up_fetch()

        self.assertIn(output_messages['ERROR_START_STOP_REQUIRES_POSITIVE'],
                      check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG) + ' --sample-type=range --sampling=-3:2:1'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_08_range_sample_with_step_parameter_greater_than_stop_parameter(self):
        self.set_up_fetch()

        self.assertIn(output_messages['ERROR_STEP_PARAMETER_SHOULD_BE_SMALLER_STOP'],
                      check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG) + ' --sample-type=range --sampling=1:3:4'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_09_range_sample_with_start_parameter_equal_to_stop(self):
        self.set_up_fetch()

        self.assertIn(output_messages['ERROR_START_PARAMETER_SHOULD_BE_SMALLER_THAN_STOP'],
                      check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG) + ' --sample-type=range --sampling=2:2:1'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_10_range_sample_with_stop_parameter_greater_than_file_list_size(self):
        self.set_up_fetch()

        self.assertIn(output_messages['ERROR_STOP_PARAMETER_SHOULD_BE_SMALLER_LIST_SIZE'],
                      check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG) + ' --sample-type=range --sampling=2:30:1'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_11_checkout_with_random_sample(self):
        self.set_up_fetch()

        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG)
                                                     + ' --sample-type=random --sampling=2:3 --seed=3'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_12_random_sample_with_frequency_less_or_equal_zero(self):
        self.set_up_fetch()

        self.assertIn(output_messages['ERROR_AMOUNT_FREQUENCY_REQUIRES_POSITIVE'],
                      check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG) + ' --sample-type=random --sampling=2:-2 --seed=3'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_13_random_sample_with_amount_parameter_greater_than_frequency(self):
        self.set_up_fetch()

        self.assertIn(output_messages['ERROR_AMOUNT_PARAMETER_SHOULD_BE_SMALLER_FREQUENCY'],
                      check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG) + ' --sample-type=random --sampling=4:2 --seed=3'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_14_random_sample_with_frequency_greater_or_equal_list_size(self):
        self.set_up_fetch()

        self.assertIn(output_messages['ERROR_FREQUENCY_PARAMETER_SHOULD_BE_SMALLER_LIST_SIZE'],
                      check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG) + ' --sample-type=random --sampling=2:10 --seed=3'))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_15_fetch_with_wrong_git_configured(self):
        self.set_up_fetch()
        change_git_in_config(os.path.join(self.tmp_dir, '.ml-git'), 'wrong-url')

        self.assertIn(output_messages['INFO_NOT_GIT_REPOSITORY'], check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG)))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_16_fetch_with_wrong_tag(self):
        self.set_up_fetch()
        wrong_tag = 'computer-vision__images__datasets-ex__10'
        self.assertIn(output_messages['INFO_PATHSPEC_KNOWN_GIT'] % wrong_tag, check_output(MLGIT_FETCH % (DATASETS, wrong_tag)))

    @pytest.mark.usefixtures('switch_to_tmp_dir', 'start_local_git_server')
    def test_17_fetch_with_invalid_retry(self):
        self.set_up_fetch()
        expected_error_message = '-2 is not in the valid range of 0 to 99999999.'
        self.assertIn(expected_error_message, check_output(MLGIT_FETCH % (DATASETS, DATASET_TAG + ' --retry=-2')))
