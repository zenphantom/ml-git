"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import base64
import json
import os
import unittest

import pytest

from ml_git.constants import EntityType, STORAGE_CONFIG_KEY, StorageType, MutabilityType
from ml_git.utils import yaml_save

dummy_api_github_url = 'https://api.github.com:443'

dummy_config = {
    EntityType.DATASETS.value: {'git': 'https://github.com/dummy/dummy_datasets_repo.git'},
    EntityType.MODELS.value: {'git': ''},
    EntityType.LABELS.value: {'git': ''},

    STORAGE_CONFIG_KEY: {
        StorageType.S3.value: {
            'mlgit-datasets': {
                'region': 'us-east-1',
                'aws-credentials': {'profile': 'default'}
            }
        }
    },
}

search_repo_url = f'{dummy_api_github_url}/search/repositories?q=dummy%2Fdummy_datasets_repo'
search_code_url = f'{dummy_api_github_url}/search/code?q=repo%3Adummy_datasets+extension%3A.spec'
dataset_content_url = f'{dummy_api_github_url}/repos/dummy_datasets_repo/contents/dataset-ex/dataset-ex.spec'
get_repo_url = f'{dummy_api_github_url.replace("api.","")}/dummy_datasets_repo'
get_tags_from_repo_url = f'{dummy_api_github_url}/repos/dummy_datasets_repo/tags'
get_spec_content_url = f'{dummy_api_github_url}/repos/dummy/dummy_datasets_repo/contents/dataset-ex/dataset-ex.spec?ref=test__dataset-ex__1'
dummy_config_remote_url = f'{dummy_api_github_url}/search/repositories?q=dummy%2Fdummy_config'
dummy_config_content_url = f'{dummy_api_github_url}/repos/dummy/dummy_config/contents//.ml-git/config.yaml'

search_repo_response = {
    'items': [
      {
        'id': 310705171,
        'name': 'dummy_datasets',
        'full_name': 'dummy_datasets',
        'private': False,
        'owner': {
          'login': 'dummy',
          'id': 24386872,
          'url': 'https://github.com/dummy_datasets_repo',
          'html_url': 'https://github.com/dummy_datasets_repo',
          'type': 'User',
          'site_admin': False
        },
        'html_url': 'https://github.com/dummy_datasets_repo',
        'url': 'https://api.github.com/repos/dummy_datasets_repo',
        'git_url': 'git://github.com/dummy_datasets.git',
        'ssh_url': 'git@github.com:dummy/dummy_datasets.git',
      }
    ]
}

user_response = {
    'login': 'dummy',
    'id': 24386872,
    'type': 'User',
    'name': 'dummy',
}

search_code_response = {
  'total_count': 1,
  'incomplete_results': False,
  'items': [
    {
      'name': 'dataset-ex.spec',
      'path': 'dataset-ex/dataset-ex.spec',
    }
  ]
}

dataset_content = {
  'name': 'dataset-ex.spec',
  'path': 'dataset-ex/dataset-ex.spec',
  'sha': '4997e46c183cbbe23bbeecbb9a336555e24a16e8',
  'size': 191,
  'type': 'file',
  'content': 'ZGF0YXNldDoNCiAgY2F0ZWdvcmllczoNCiAgLSB0ZXN0DQogIG1hbmlmZXN0\n'
             'Og0KICAgIGFtb3VudDogMg0KICAgIGZpbGVzOiBNQU5JRkVTVC55YW1sDQog\n'
             'ICAgc2l6ZTogMTggQnl0ZXMNCiAgICBzdG9yZTogczNoOi8vbWxnaXQNCiAg\n'
             'bXV0YWJpbGl0eTogZmxleGlibGUNCiAgbmFtZTogZGF0YXNldC1leA0KICB2\n'
             'ZXJzaW9uOiAzDQo=\n',
  'encoding': 'base64',
}

repo = {
  'login': 'dummy',
  'id': 24386872,
  'type': 'User',
  'site_admin': False,
  'name': 'dummy',
}

tags = [
  {
    'name': 'test__dataset-ex__1',
  }
]

content_from_tag = {
  'name': 'dataset-ex.spec',
  'path': 'dataset-ex/dataset-ex.spec',
  'sha': '73c20aceff15b737b37b674e84e321b6d4a461e5',
  'size': 203,
  'type': 'file',
  'content': 'ZGF0YXNldDoNCiAgY2F0ZWdvcmllczoNCiAgLSB0ZXN0DQogIG1hbmlmZXN0\n'
             'Og0KICAgIGFtb3VudDogMQ0KICAgIGZpbGVzOiBNQU5JRkVTVC55YW1sDQog\n'
             'ICAgc2l6ZTogOSBCeXRlcw0KICAgIHN0b3JhZ2U6IHMzaDovL21sZ2l0LXRl\n'
             'c3QtbHVjYXMNCiAgbXV0YWJpbGl0eTogZmxleGlibGUNCiAgbmFtZTogZGF0\n'
             'YXNldC1leA0KICB2ZXJzaW9uOiAxDQo=\n',
  'encoding': 'base64',
}

config_repo_response = {
    'items': [
      {
        'id': 310705171,
        'name': 'dummy_config',
        'full_name': 'dummy_config',
        'private': False,
        'owner': {
          'login': 'dummy',
          'id': 24386872,
          'url': 'https://github.com/dummy/dummy_config',
          'html_url': 'https://github.com/dummy/dummy_config',
          'type': 'User',
          'site_admin': False
        },
        'html_url': 'https://github.com/dummy/dummy_config',
        'url': 'https://api.github.com/repos/dummy/dummy_config',
        'git_url': 'git://github.com/dummy/dummy_config.git',
        'ssh_url': 'git@github.com:dummy/dummy/dummy_config.git',
      }
    ]
}

config_content_response = {
  'name': 'config.yaml',
  'path': '.ml-git/config.yaml',
  'sha': 'ebd3e03e034e3bde8799083e7ab76e058581c4a7',
  'size': 379,
  'type': 'file',
  'content': base64.b64encode(json.dumps(dummy_config).encode('ascii')).decode('utf-8'),
  'encoding': 'base64',
}

HEADERS = {
    'access-control-allow-origin': '*',
    'access-control-expose-headers': 'ETag, Link, Location, Retry-After, X-GitHub-OTP, X-RateLimit-Limit,'
                                     ' X-RateLimit-Remaining, X-RateLimit-Used, X-RateLimit-Reset, X-OAuth-Scopes,'
                                     ' X-Accepted-OAuth-Scopes, X-Poll-Interval, X-GitHub-Media-Type,'
                                     ' Deprecation, Sunset',
    'cache-control': 'private, max-age=60, s-maxage=60',
    'content-security-policy': 'default-src \'none\'',
    'content-type': 'application/json; charset=utf-8',
    'vary': 'Accept, Authorization, Cookie, X-GitHub-OTP, Accept-Encoding, Accept, X-Requested-With',
    'x-github-media-type': 'github.v3; format=json',
    'x-oauth-scopes': 'public_repo, repo:status, repo_deployment',
    'transfer-encoding': 'chunked'
}


@pytest.mark.usefixtures('tmp_dir')
class ApiTestCases(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def requests_mock(self, requests_mock):
        self.requests_mock = requests_mock

    def setUp(self):
        from ml_git import api
        self.manager = api.init_entity_manager('github_token', 'https://api.github.com')
        self.config_path = os.path.join(self.tmp_dir, 'config.yaml')
        yaml_save(dummy_config, self.config_path)
        self.requests_mock.get(search_repo_url, status_code=200, headers=HEADERS, json=search_repo_response)
        self.requests_mock.get(search_code_url, status_code=200, headers=HEADERS, json=search_code_response)
        self.requests_mock.get(dataset_content_url, status_code=200, headers=HEADERS, json=dataset_content)
        self.requests_mock.get(get_repo_url, status_code=200, headers=HEADERS, json=repo)
        self.requests_mock.get(get_tags_from_repo_url, status_code=200, headers=HEADERS, json=tags)
        self.requests_mock.get(get_spec_content_url, status_code=200, headers=HEADERS, json=content_from_tag)

    def test_init_entity_manager(self):
        self.assertIsNotNone(self.manager)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_entities_from_config_path(self):
        entities = self.manager.get_entities(config_path=self.config_path)
        self.assertTrue(len(entities) == 1)
        self.assertEqual(entities[0].name, 'dataset-ex')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_entities_from_repo_name(self):
        self.requests_mock.get(dummy_config_remote_url, status_code=200, headers=HEADERS, json=config_repo_response)
        self.requests_mock.get(dummy_config_content_url, status_code=200, headers=HEADERS, json=config_content_response)
        entities = self.manager.get_entities(repo_name='dummy/dummy_config')
        self.assertTrue(len(entities) == 1)
        self.assertEqual(entities[0].name, 'dataset-ex')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_entity_spec_path(self):
        self.requests_mock.get(dummy_config_remote_url, status_code=200, headers=HEADERS, json=config_repo_response)
        self.requests_mock.get(search_code_url, status_code=200, headers=HEADERS, json=search_code_response)
        repository = self.manager._manager.find_repository('dummy/dummy_datasets_repo')
        spec_path = self.manager._get_entity_spec_path(repository, 'dataset-ex')
        self.assertEquals('dataset-ex/dataset-ex.spec', spec_path)
        with self.assertRaises(Exception):
            self.manager._get_entity_spec_path(repository, 'worng-dataset-name')

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_get_entity_versions(self):
        self.requests_mock.get(dummy_config_remote_url, status_code=200, headers=HEADERS, json=config_repo_response)
        self.requests_mock.get(search_code_url, status_code=200, headers=HEADERS, json=search_code_response)
        entity_versions = self.manager.get_entity_versions('dataset-ex', 'dummy/dummy_datasets_repo')
        self.assertTrue(len(entity_versions) == 1)
        self.assertEquals(entity_versions[0].version, 3)
        self.assertEquals(entity_versions[0].tag, 'test__dataset-ex__3')
        self.assertEquals(entity_versions[0].mutability, MutabilityType.FLEXIBLE.value)
        self.assertEquals(entity_versions[0].categories, ['test'])
        self.assertEquals(entity_versions[0].storage_type, StorageType.S3H.value)
        self.assertEquals(entity_versions[0].bucket, 'mlgit')
        self.assertEquals(entity_versions[0].amount, 2)
        self.assertEquals(entity_versions[0].size, '18 Bytes')
