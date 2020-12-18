"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import importlib

from ml_git import log
from ml_git.plugin_interface.data_plugin_constants import SPEC_PLUGIN_KEY


class PluginCaller:

    def __init__(self, manifest):
        self.plugin_name = manifest.get(SPEC_PLUGIN_KEY, '')
        self.package = self.__import_plugin()

    def __import_plugin(self):
        if not self.plugin_name:
            return None
        try:
            package = importlib.import_module(self.plugin_name)
            return package
        except ImportError as e:
            log.error(str(e), class_name=self.__class__.__name__)
            return None

    def call(self, name, *args, **kwargs):
        if not self.package:
            return

        attribute = getattr(self.package, name, None)
        if attribute:
            return attribute(*args, **kwargs)
