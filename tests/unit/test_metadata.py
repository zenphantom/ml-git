"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil
import unittest
from copy import deepcopy
from unittest import mock

import pytest
from git import GitError, Repo

from ml_git.metadata import Metadata
from ml_git.repository import Repository
from ml_git.utils import clear
from ml_git.utils import yaml_save, ensure_path_exists

files_mock = {'zdj7Wm99FQsJ7a4udnx36ZQNTy7h4Pao3XmRSfjo4sAbt9g74': {'1.jpg'},
              'zdj7WnVtg7ZgwzNxwmmDatnEoM3vbuszr3xcVuBYrcFD6XzmW': {'2.jpg'},
              'zdj7Wi7qy2o3kgUC72q2aSqzXV8shrererADgd6NTP9NabpvB': {'3.jpg'},
              'zdj7We7FUbukkozcTtYgcsSnLWGqCm2PfkK53nwJWLHEtuef4': {'6.jpg'},
              'zdj7WZzR8Tw87Dx3dm76W5aehnT23GSbXbQ9qo73JgtwREGwB': {'7.jpg'},
              'zdj7WfQCZgACUxwmhVMBp4Z2x6zk7eCMUZfbRDrswQVUY1Fud': {'8.jpg'},
              'zdj7WdjnTVfz5AhTavcpsDT62WiQo4AeQy6s4UC1BSEZYx4NP': {'9.jpg'},
              'zdj7WXiB8QrNVQ2VABPvvfC3VW6wFRTWKvFhUW5QaDx6JMoma': {'10.jpg'}}

spec = 'dataset-ex'
spec_2 = 'dataset-ex-2'
index_path = './mdata'
config = {
    'mlgit_path': './mdata',
    'mlgit_conf': 'config.yaml',

    'dataset': {
        'git': os.path.join(os.getcwd(), 'git_local_server.git'),
    },
    'labels': {
        'git': os.path.join(os.getcwd(), 'git_local_server.git'),
    },
    'model': {
        'git': os.path.join(os.getcwd(), 'git_local_server.git'),
    },


    'store': {
        's3': {
            'mlgit-datasets': {
                'region': 'us-east-1',
                'aws-credentials': {'profile': 'mlgit'}
            }
        }
    },

    'verbose': 'info',
}

repotype = 'dataset'

metadata_config = {
    'dataset': {
        'categories': 'images',
        'manifest': {
            'files': 'MANIFEST.yaml',
            'store': 's3h://ml-git-datasets'
        },
        'name': 'dataset_ex',
        'version': 1
    }
}


@pytest.mark.usefixtures('test_dir')
class MetadataTestCases(unittest.TestCase):

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_test_dir')
    def test_init(self):
        m = Metadata(spec, self.test_dir, config, repotype)
        m.init()
        self.assertTrue(m.check_exists())
        clear(m.path)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_test_dir')
    def test_metadata_tag(self):
        m = Metadata(spec, index_path, config, repotype)
        tag = m.metadata_tag(metadata_config)
        self.assertEqual(tag, 'images__dataset_ex__1')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_test_dir')
    def test_tag_exist(self):
        mdpath = os.path.join(self.test_dir, 'metadata')
        specpath = 'dataset-ex'
        ensure_path_exists(os.path.join(mdpath, specpath))
        shutil.copy('hdata/dataset-ex.spec', os.path.join(mdpath, specpath) + '/dataset-ex.spec')
        manifestpath = os.path.join(os.path.join(mdpath, specpath), 'MANIFEST.yaml')
        yaml_save(files_mock, manifestpath)

        config['mlgit_path'] = self.test_dir
        m = Metadata(specpath, mdpath, config, repotype)
        r = Repository(config, repotype)
        r.init()

        fullmetadatapath, categories_subpath, metadata = m.tag_exists(self.test_dir)
        self.assertFalse(metadata is None)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_test_dir')
    def test_clone_config_repo(self):
        m = Metadata('', self.test_dir, config, repotype)
        m.clone_config_repo()
        self.assertTrue(m.check_exists())

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_test_dir')
    def test_get_tag(self):
        mdpath = os.path.join(self.test_dir, 'metadata')
        specpath = 'dataset-ex'
        ensure_path_exists(os.path.join(mdpath, specpath))
        shutil.copy('hdata/dataset-ex.spec', os.path.join(mdpath, specpath) + '/dataset-ex.spec')
        manifestpath = os.path.join(os.path.join(mdpath, specpath), 'MANIFEST.yaml')
        yaml_save(files_mock, manifestpath)

        config['mlgit_path'] = self.test_dir
        m = Metadata(specpath, mdpath, config, repotype)
        r = Repository(config, repotype)
        r.init()

        tag_list = ['computer__images__dataset-ex__1']
        with mock.patch('ml_git.metadata.Metadata.list_tags', return_value=tag_list):
            target_tag = m.get_tag(specpath, -1)
        self.assertEqual(target_tag, tag_list[0])
        clear(m.path)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_test_dir')
    def test_get_target_tag(self):
        tags = ['computer__images__dataset-ex__1',
                'computer__images__dataset-ex__2',
                'computer__videos__dataset-ex__1']
        m = Metadata('', self.test_dir, config, repotype)
        self.assertRaises(RuntimeError, lambda: m._get_target_tag(tags, 'dataset-ex', -1))
        self.assertRaises(RuntimeError, lambda: m._get_target_tag(tags, 'dataset-ex', 1))
        self.assertRaises(RuntimeError, lambda: m._get_target_tag(tags, 'dataset-wrong', 1))
        self.assertEqual(m._get_target_tag(tags, 'dataset-ex', 2), 'computer__images__dataset-ex__2')
        clear(m.path)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_test_dir')
    def test_clone_empty_config_repo(self):
        config = {
            'mlgit_path': './mdata',
            'mlgit_conf': 'config.yaml',
            'verbose': 'info',
            'dataset': {'git': '', },
            'labels': {'git': '', },
            'model': {'git': '', }, }

        m = Metadata('', self.test_dir, config, repotype)
        m.clone_config_repo()
        self.assertFalse(m.check_exists())

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_test_dir')
    def test_blank_remote_url(self):
        config_cp = deepcopy(config)
        config_cp['dataset']['git'] = ''
        m = Metadata(spec, self.test_dir, config_cp, repotype)
        self.assertRaises(GitError, m.validate_blank_remote_url)
        clear(m.path)

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_test_dir')
    def test_delete_git_reference(self):
        m = Metadata(spec, self.test_dir, config, repotype)
        m.init()

        for url in Repo(m.path).remote().urls:
            self.assertNotEqual(url, '')

        self.assertTrue(m.delete_git_reference())

        for url in Repo(m.path).remote().urls:
            self.assertEqual(url, '')

    @pytest.mark.usefixtures('start_local_git_server', 'switch_to_test_dir', 'change_branch_name')
    def test_default_branch(self):
        default_branch_for_empty_repo = 'master'
        new_branch = 'main'
        m = Metadata('', self.test_dir, config, repotype)
        m.init()
        self.assertTrue(m.check_exists())
        self.assertEqual(m.get_default_branch(), default_branch_for_empty_repo)
        self.change_branch(m.path, new_branch)
        self.assertNotEqual(m.get_default_branch(), default_branch_for_empty_repo)
        self.assertEqual(m.get_default_branch(), new_branch)
        clear(m.path)
