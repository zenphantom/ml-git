"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.utils import ensure_path_exists, yaml_load
from mlgit.hashfs import HashFS
import os

class Cache(HashFS):
	def __init__(self, cachepath, datapath, manifest):
		super(Cache, self).__init__(cachepath)
		self.__datapath = datapath
		self.__manifest = manifest

	def update(self):
		files = yaml_load(self.__manifest)
		for key in files:
			file = files[key]

			srcfile = os.path.join(self.__datapath, file)
			self.link(key, srcfile)

