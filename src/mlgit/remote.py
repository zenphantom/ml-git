"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.utils import yaml_load
from mlgit.store import store_factory
from mlgit.index import Index, MultihashIndex
from mlgit.utils import yaml_load, ensure_path_exists, json_load
from mlgit.spec import spec_parse
from mlgit import log
import os
import shutil


class Remote(object):
	def __init__(self, objectspath, config, repotype="dataset"):
		# self.__path = objectspath
		self.__config = config
		self.__repotype = repotype

	def push(self, idxstore, objectpath, specfile):
		repotype = self.__repotype

		spec = yaml_load(specfile)
		manifest = spec[repotype]["manifest"]
		store = store_factory(self.__config, manifest["store"])

		with open(idxstore, 'r') as f:
			while True:
				obj = f.readline().strip()
				if not obj: break
				log.info("Remote: push blob [%s] to [%s]" % (obj, manifest["store"]))
				# Get obj from filesystem
				objpath = Index._get_hashpath(objectpath, obj)
				list = store.file_store(obj, objpath)
		os.unlink(idxstore)

	def haspath(self, path, key):
		objpath = Index._get_hashpath(path, key)
		dirname = os.path.dirname(objpath)
		ensure_path_exists(dirname)
		return objpath

	def _fetch_blob(self, key, objpath, store):
		if os.path.exists(objpath) == False:
			log.info("Remote: downloading blob [%s]" % (key))
			if store.get(objpath, key) == False:
				log.error("Remote: error downloading blob [%s]")
				return False
		# else: check integrity of file on disk?
		return True

	def fetch(self, objectpath, metadatapath, spec):
		repotype = self.__repotype

		categories_path, specname, version = spec_parse(spec)

		# retrieve specfile from metadata to get store
		specpath = os.path.join(metadatapath, categories_path, specname + '.spec')
		spec = yaml_load(specpath)
		manifest = spec[repotype]["manifest"]
		store = store_factory(self.__config, manifest["store"])

		manifestfile = "MANIFEST.yaml"
		manifestpath = os.path.join(metadatapath, categories_path, manifestfile)
		files = yaml_load(manifestpath)
		for key in files:
			objpath = self.haspath(objectpath, key)

			if self._fetch_blob(key, objpath, store) == False: return

			links = json_load(objpath)
			for link in links["Links"]:
				h = link["Hash"]
				objpath = self.haspath(objectpath, h)
				if self._fetch_blob(h, objpath, store) == False: return

	def search_spec_file(self, spec):
		repotype = self.__repotype
		try:
			dir = os.sep.join([repotype, spec])
			files = os.listdir(os.sep.join([repotype, spec]))
		except Exception as e: #TODO: search "." path as well
			dir = spec
			try:
				files = os.listdir(spec)
			except:
				return None, None

		for file in files:
			if spec in file:
				log.debug("search spec file: found [%s]-[%s]" % (dir, file))
				return dir, file

		return None, None

	def get(self, cachepath, metadatapath, objectpath, spec):
		repotype = self.__repotype

		categories_path, specname, version = spec_parse(spec)

		wspath, spec= self.search_spec_file(specname)
		if wspath is None:
			wspath = os.path.join(repotype, categories_path)
			ensure_path_exists(wspath)

		midx = MultihashIndex(specname, objectpath)
		manifestfile = "MANIFEST.yaml"
		manifestpath = os.path.join(metadatapath, categories_path, manifestfile)
		files = yaml_load(manifestpath)
		mfiles={}
		for key in files:
			objpath = self.haspath(cachepath, key)

			if os.path.exists(objpath) == False:
				midx._get_file(key, os.path.dirname(objpath), key)


			file = files[key]
			mfiles[file] = key
			filepath = os.path.join(wspath, file)

			if os.path.exists(filepath):
				os.unlink(filepath)
			ensure_path_exists(os.path.dirname(filepath))
			os.link(objpath, filepath)

		# Check files that have been removed (present in wskpace and not in MANIFEST)
		for root, dirs, files in os.walk(wspath):
			relative_path = root[len(wspath) + 1:]

			for file in files:
				if "README.md" in file: continue
				if ".spec" in file: continue
				if 'MANIFEST' in file: continue

				fullpath = os.path.join(relative_path, file)
				if fullpath not in mfiles:
					os.unlink(os.path.join(root, file))
					log.debug("removing %s" % (fullpath))

		for md in [ "README.md", specname + ".spec" ]:
			mdpath = os.path.join(metadatapath, categories_path, md)
			mddst = os.path.join(wspath, md)
			shutil.copy2(mdpath, mddst)

