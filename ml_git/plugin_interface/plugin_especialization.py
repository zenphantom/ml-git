"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import importlib

from ml_git import log


class PluginCaller:
    SPEC_PLUGIN_KEY = 'data-plugin'

    def __init__(self, manifest):
        self.plugin_name = manifest.get(self.SPEC_PLUGIN_KEY, '')
        self.package = self.__import_plugin()

    def __import_plugin(self):
        if not self.plugin_name:
            return None
        try:
            package = importlib.import_module(self.plugin_name)
            return package
        except ImportError as e:
            log.error(e, class_name=type(self).__name__)
            return None

    def call(self, name, *args, **kwargs):
        if not self.package:
            return

        attribute = getattr(self.package, name, None)
        if attribute:
            return attribute(*args, **kwargs)
