"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import os
import unittest

import pytest

from ml_git.ml_git_message import output_messages
from tests.integration.commands import MLGIT_INIT, MLGIT_CONFIG
from tests.integration.helper import check_output


@pytest.mark.usefixtures('tmp_dir')
class ConfigAcceptanceTests(unittest.TestCase):
    threads_per_core = 5
    push_threads_count = os.cpu_count() * threads_per_core
    expected_result = "config:\n{'batch_size': 20,\n 'cache_path': '',\n 'datasets': {'git': ''}," \
                      "\n 'index_path': '',\n 'labels': {'git': ''},\n 'metadata_path': '',\n 'mlgit_conf': 'config.yaml'," \
                      "\n 'mlgit_path': '.ml-git',\n 'models': {'git': ''},\n 'object_path': ''," \
                      "\n 'push_threads_count': "+str(push_threads_count)+",\n 'refs_path': ''," \
                      "\n 'storage': {'s3': {'mlgit-datasets': {'aws-credentials': {'profile': 'default'}," \
                      "\n                                       'region': 'us-east-1'}}},\n 'verbose': 'info'}"

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_01_config_command(self):
        self.assertIn(output_messages['INFO_INITIALIZED_PROJECT_IN'] % self.tmp_dir, check_output(MLGIT_INIT))
        self.assertIn(self.expected_result, check_output(MLGIT_CONFIG))
