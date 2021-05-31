"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import unittest

import pytest

from ml_git import log
from ml_git.constants import LOG_FILES_PATH, LOG_FILE_NAME
from ml_git.log import init_logger, set_level
from ml_git.ml_git_message import output_messages


@pytest.mark.usefixtures('tmp_dir')
class LogTestCases(unittest.TestCase):
    logs = {
        'DEBUG': log.debug,
        'ERROR': log.error,
        'WARN': log.warn,
        'INFO': log.info,
        'FATAL': log.fatal
    }

    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

    def check_log(self, log_type, message):
        log_file_path = os.path.join(self.tmp_dir, LOG_FILES_PATH)

        init_logger()
        debug_level = 'debug'
        if log_type.lower() == debug_level:
            set_level(debug_level)

        self.logs[log_type](message)
        out, err = self.capfd.readouterr()

        if log_type == 'ERROR':
            file_location = output_messages['ERROR_FIND_FILE_PATH_LOCATION'] % LOG_FILE_NAME
            self.assertIn(file_location, out)

        self.assertIn(message, err)
        self.assertTrue(os.path.exists(log_file_path))

        log_file = os.path.join(log_file_path, LOG_FILE_NAME)
        self.assertTrue(os.path.exists(log_file))
        with open(log_file, 'r') as lf:
            self.assertIn(message, lf.read())

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_log_info(self):
        message = 'Check log info'
        self.check_log('INFO', message)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_log_debug(self):
        message = 'Check log debug'
        self.check_log('DEBUG', message)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_log_warn(self):
        message = 'Check log warning'
        self.check_log('WARN', message)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_log_error(self):
        message = 'Check log error'
        self.check_log('ERROR', message)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_log_fatal(self):
        message = 'Check log fatal'
        self.check_log('FATAL', message)
