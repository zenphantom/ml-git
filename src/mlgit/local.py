"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.store import store_factory
from mlgit.hashfs import HashFS, MultihashFS
from mlgit.utils import yaml_load, ensure_path_exists, json_load
from mlgit.spec import spec_parse, search_spec_file
from mlgit import log
import os
import shutil


class LocalRepository(MultihashFS):
	def __init__(self, config, objectspath, repotype="dataset", blocksize=256*1024, levels=2):
		super(LocalRepository, self).__init__(objectspath, blocksize, levels)
		self.__config = config
		self.__repotype = repotype

	def push(self, idxstore, objectpath, specfile):
		repotype = self.__repotype

		spec = yaml_load(specfile)
		manifest = spec[repotype]["manifest"]
		store = store_factory(self.__config, manifest["store"])

		idx = MultihashFS(idxstore)
		objs = idx.get_log()
		for obj in objs:
			log.info("LocalRepository: push blob [%s] to [%s]" % (obj, manifest["store"]))
			# Get obj from filesystem
			objpath = self._keypath(obj)
			list = store.file_store(obj, objpath)
		idx.reset_log()

	def hashpath(self, path, key):
		objpath = self._get_hashpath(key, path)
		dirname = os.path.dirname(objpath)
		ensure_path_exists(dirname)
		return objpath

	def _fetch_blob(self, key, keypath, store):
		ensure_path_exists(os.path.dirname(keypath))
		log.info("LocalRepository: downloading blob [%s]" % (key))
		for i in range(3):
			if store.get(keypath, key) == True:
				return True
			log.error("LocalRepository: error downloading blob [%s] at attempt [%d]" % (key, i))
			time.sleep(10)
		log.error("LocalRepository: permanent failure to download blob [%s]" % (key))
		return False

	def fetch(self, metadatapath, tag):
		repotype = self.__repotype

		categories_path, specname, version = spec_parse(tag)

		# retrieve specfile from metadata to get store
		specpath = os.path.join(metadatapath, categories_path, specname + '.spec')
		spec = yaml_load(specpath)
		manifest = spec[repotype]["manifest"]
		store = store_factory(self.__config, manifest["store"])

		# retrieve manifest from metadata to get all files of version tag
		manifestfile = "MANIFEST.yaml"
		manifestpath = os.path.join(metadatapath, categories_path, manifestfile)
		files = yaml_load(manifestpath)

		# TODO: move as a 'deep_copy' function into hashfs ?
		for key in files:
			# blob file describing IPLD links
			log.debug("LocalRepository: getting key [%s]" % (key))
			if self._exists(key) == False:
				keypath = self._keypath(key)
				if self._fetch_blob(key, keypath, store) == False:
					return

			# retrieve all links described in the retrieved blob
			links = self.load(key)
			for olink in links["Links"]:
				key = olink["Hash"]
				log.debug("LocalRepository: getting [%s]" % (key))
				if self._exists(key) == False:
					keypath = self._keypath(key)
					if self._fetch_blob(key, keypath, store) == False:
						return

	def _update_cache(self, cache, key):
		# determine whether file is already in cache, if not, get it
		if cache.exists(key) == False:
			cfile = cache._keypath(key)
			ensure_path_exists(os.path.dirname(cfile))
			super().get(key, cfile)

	def _update_links_wspace(self, cache, files, key, wspath, mfiles):
		# for all concrete files specified in manifest, create a hard link into workspace
		for file in files:
			mfiles[file] = key
			filepath = os.path.join(wspath, file)
			cache.ilink(key, filepath)

	def _remove_unused_links_wspace(self, wspath, mfiles):
		for root, dirs, files in os.walk(wspath):
			relative_path = root[len(wspath) + 1:]

			for file in files:
				if "README.md" in file: continue
				if ".spec" in file: continue

				fullpath = os.path.join(relative_path, file)
				if fullpath not in mfiles:
					os.unlink(os.path.join(root, file))
					log.debug("removing %s" % (fullpath))

	def _update_metadata(self, fullmdpath, wspath, specname):
		for md in [ "README.md", specname + ".spec" ]:
			mdpath = os.path.join(fullmdpath, md)
			if os.path.exists(mdpath) == False: continue
			mddst = os.path.join(wspath, md)
			shutil.copy2(mdpath, mddst)

	def get(self, cachepath, metadatapath, objectpath, wspath, tag):
		categories_path, specname, version = spec_parse(tag)


		# get all files for specific tag
		manifestpath = os.path.join(metadatapath, categories_path, "MANIFEST.yaml")

		cache = HashFS(cachepath)

		# copy all files defined in manifest from objects to cache (if not there yet) then hard links to workspace
		mfiles = {}
		objfiles = yaml_load(manifestpath)
		for key in objfiles:
			# check file is in objects ; otherwise critical error (should have been fetched at step before)
			if self._exists(key) == False:
				log.error("LocalRepository: blob [%s] not found. exiting...")
				return
			self._update_cache(cache, key)
			self._update_links_wspace(cache, objfiles[key], key, wspath, mfiles)

		# Check files that have been removed (present in wskpace and not in MANIFEST)
		self._remove_unused_links_wspace(wspath, mfiles)

		# Update metadata in workspace
		fullmdpath = os.path.join(metadatapath, categories_path)
		self._update_metadata(fullmdpath, wspath, specname)



