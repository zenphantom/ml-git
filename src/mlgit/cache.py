"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.utils import ensure_path_exists, yaml_load
from mlgit.multihash import create_hashpath
from mlgit import log
import os
import errno

class Cache(object):
	def __init__(self, cachepath, datapath, manifest):
		self.__cachepath = cachepath
		ensure_path_exists(cachepath)
		self.__datapath = datapath
		self.__manifest = manifest

	def update(self):
		files = yaml_load(self.__manifest)
		for key in files:
			file = files[key]
			src = os.path.join(self.__datapath, file)
			hdir = create_hashpath(self.__cachepath, key)
			dst = os.path.join(hdir, key)

			if os.path.exists(dst) == True:
				log.debug("Cache: entry cache [%s] already exists for [%s]. possible duplicate." % (key, file))
				os.unlink(src)
				os.link(dst, src)
				return

			log.info("Cache: creating entry cache [%s] for [%s]" % (key, file))
			os.link(src, dst)

	def fsck(self, objects):
		pass


if __name__=="__main__":
	from mlgit.log import init_logger
	init_logger()

	c = Cache(".ml-git/dataset/cache", "dataset/dataset-ex", ".ml-git/dataset/index/files/dataset-ex/MANIFEST.yaml")
	c.update()