"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import pathlib
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_CHECKOUT, MLGIT_PUSH, MLGIT_COMMIT, MLGIT_ADD
from tests.integration.helper import ML_GIT_DIR, MLGIT_ENTITY_INIT, ERROR_MESSAGE, \
    add_file, GIT_PATH, check_output, clear, init_repository, DATASETS, DATASET_NAME, DATASET_TAG


@pytest.mark.usefixtures('tmp_dir', 'aws_session')
class CheckoutTagAcceptanceTests(unittest.TestCase):

    def set_up_checkout(self, entity):
        init_repository(entity, self)
        add_file(self, entity, '', 'new')
        metadata_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')
        self.assertIn(output_messages['INFO_COMMIT_REPO'] % (metadata_path, os.path.join('computer-vision', 'images', entity + '-ex')),
                      check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        head_path = os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'refs', entity + '-ex', 'HEAD')
        self.assertTrue(os.path.exists(head_path))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        self._clear_workspace(entity)

    def check_amount_of_files(self, entity_type, expected_files):
        entity_dir = os.path.join(self.tmp_dir, entity_type, 'computer-vision', 'images', entity_type+'-ex')
        self.assertTrue(os.path.exists(entity_dir))
        file_count = 0
        for path in pathlib.Path(entity_dir).iterdir():
            if path.is_file():
                file_count += 1
        self.assertEqual(file_count, expected_files)

    def check_metadata(self):
        objects = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'objects')
        refs = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'refs')
        cache = os.path.join(self.tmp_dir, ML_GIT_DIR, DATASETS, 'cache')
        spec_file = os.path.join(self.tmp_dir, DATASETS, 'computer-vision', 'images', DATASET_NAME, 'datasets-ex.spec')

        self.assertTrue(os.path.exists(objects))
        self.assertTrue(os.path.exists(refs))
        self.assertTrue(os.path.exists(cache))
        self.assertTrue(os.path.exists(spec_file))

    def _create_new_tag(self, entity, file_name):
        add_file(self, entity, '', file_name)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', '--version=2')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))

    def _clear_workspace(self, entity):
        workspace = os.path.join(self.tmp_dir, entity)
        clear(os.path.join(self.tmp_dir, ML_GIT_DIR, entity))
        clear(workspace)
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))

    def _create_entity(self, entity, category):
        init_repository(entity, self, category=category)
        self._create_new_tag(entity, 'new')
        self._clear_workspace(entity)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_01_checkout_with_entity_name(self):
        entity = DATASETS
        init_repository(entity, self)
        self._create_new_tag(entity, 'new')
        self._clear_workspace(entity)
        self.assertIn(output_messages['INFO_CHECKOUT_LATEST_TAG'] % 'computer-vision__images__datasets-ex__2',
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_NAME)))
        file = os.path.join(self.tmp_dir, DATASETS, 'computer-vision', 'images', DATASET_NAME, 'newfile0')
        self.check_metadata()
        self.check_amount_of_files(DATASETS, 6)
        self.assertTrue(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_02_checkout_with_wrong_entity_name(self):
        self.set_up_checkout(DATASETS)
        self.assertIn(output_messages['ERROR_WITHOUT_TAG_FOR_THIS_ENTITY'],
                      check_output(MLGIT_CHECKOUT % (DATASETS, 'dataset-wrong')))
        file = os.path.join(self.tmp_dir, DATASETS, 'computer-vision', 'images', DATASET_NAME, 'newfile0')
        self.assertFalse(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_03_checkout_with_two_entities_wit_same_name(self):
        entity = DATASETS
        self._create_entity(entity, 'images')
        clear(os.path.join(self.tmp_dir, '.ml-git'))
        self._create_entity(entity, 'video')
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))
        self.assertIn(output_messages['ERROR_MULTIPLES_ENTITIES_WITH_SAME_NAME'] +
                      '\tcomputer-vision__images__datasets-ex__2\n\tcomputer-vision__video__datasets-ex__2',
                      check_output(MLGIT_CHECKOUT % (DATASETS, DATASET_NAME)))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_04_checkout_with_version_number(self):
        self.set_up_checkout(DATASETS)
        self.assertIn(output_messages['INFO_CHECKOUT_TAG'] % DATASET_TAG,
                      check_output(MLGIT_CHECKOUT % (DATASETS, 'datasets-ex --version=1')))
        file = os.path.join(self.tmp_dir, DATASETS, 'computer-vision', 'images', DATASET_NAME, 'newfile0')
        self.check_metadata()
        self.check_amount_of_files(DATASETS, 6)
        self.assertTrue(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_05_checkout_with_wrong_version_number(self):
        self.set_up_checkout(DATASETS)
        self.assertIn(output_messages['ERROR_WRONG_VERSION_NUMBER_TO_CHECKOUT'] % (DATASET_TAG),
                      check_output(MLGIT_CHECKOUT % (DATASETS, 'datasets-ex --version=10')))
        file = os.path.join(self.tmp_dir, DATASETS, 'computer-vision', 'images', DATASET_NAME, 'newfile0')
        self.assertFalse(os.path.exists(file))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_06_checkout_with_two_entities_wit_same_name_and_version(self):
        entity = DATASETS
        self._create_entity(entity, 'images')
        clear(os.path.join(self.tmp_dir, '.ml-git'))
        self._create_entity(entity, 'video')
        self.assertIn(output_messages['INFO_METADATA_INIT'] % (
            os.path.join(self.tmp_dir, GIT_PATH), os.path.join(self.tmp_dir, ML_GIT_DIR, entity, 'metadata')),
                      check_output(MLGIT_ENTITY_INIT % entity))
        self.assertIn(output_messages['ERROR_MULTIPLES_ENTITIES_WITH_SAME_NAME'] +
                      '\tcomputer-vision__images__datasets-ex__2\n\tcomputer-vision__video__datasets-ex__2',
                      check_output(MLGIT_CHECKOUT % (DATASETS, 'datasets-ex --version=2')))

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_tmp_dir')
    def test_07_checkout_without_clear_workspace(self):
        entity = DATASETS
        init_repository(entity, self)
        self._create_new_tag(entity, 'new')
        with open(os.path.join(self.tmp_dir, entity, entity+'-ex', 'newfile-tag2'), 'wt') as z:
            z.write('0' * 100)
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_ADD % (entity, entity + '-ex', '--bumpversion')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_COMMIT % (entity, entity + '-ex', '')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_PUSH % (entity, entity + '-ex')))
        self.assertNotIn(ERROR_MESSAGE, check_output(MLGIT_CHECKOUT % (entity, 'computer-vision__images__datasets-ex__2')))
        file = os.path.join(self.tmp_dir, entity, 'computer-vision', 'images', DATASET_NAME, 'newfile0')
        self.check_metadata()
        self.check_amount_of_files(entity, 6)
        self.assertTrue(os.path.exists(file))
