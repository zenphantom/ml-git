"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
from unittest import mock

import pytest

from ml_git.error_handler import error_handler, pass_error_to_handlers


@pytest.mark.usefixtures('tmp_dir')
class ErrorHandlerTestCases(unittest.TestCase):

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_error_handler_success(self):
        with mock.patch('ml_git.error_handler.pass_error_to_handlers', return_value=0):
            exit_code = error_handler(error=KeyError())
            self.assertEquals(exit_code, 0)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_error_handler_fail(self):
        with mock.patch('ml_git.error_handler.pass_error_to_handlers', return_value=1):
            exit_code = error_handler(error=KeyError())
            self.assertEquals(exit_code, 1)

    @pytest.mark.usefixtures('switch_to_tmp_dir')
    def test_pass_error_to_handlers(self):
        with mock.patch('pkg_resources.iter_entry_points', return_value={}):
            exit_code = pass_error_to_handlers(error=KeyError())
            self.assertEquals(exit_code, 1)
