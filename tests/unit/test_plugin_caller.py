"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest

from ml_git.plugin_interface.plugin_especialization import PluginCaller


class PluginCallerTestCases(unittest.TestCase):

    def test_import_plugin(self):
        manifest = {'data-plugin': 'random'}
        caller = PluginCaller(manifest)
        self.assertIsNotNone(caller)
        self.assertIsNotNone(caller.package)

    def test_import_invalid_plugin(self):
        manifest = {'data-plugin': 'invalid_plugin'}
        caller = PluginCaller(manifest)
        self.assertIsNotNone(caller)
        self.assertIsNone(caller.package)

    def test_call(self):
        manifest = {'data-plugin': 'random'}
        caller = PluginCaller(manifest)
        start, limit = (0, 2)
        value = caller.call('randint', start, limit)
        self.assertTrue(value in range(start, limit+1))

    def test_invalid_call(self):
        manifest = {'data-plugin': 'random'}
        caller = PluginCaller(manifest)
        start, limit = (0, 2)
        value = caller.call('invalid_method', start, limit)
        self.assertIsNone(value)
