"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log
from mlgit.config import index_path, objects_path, cache_path, metadata_path, refs_path
from mlgit.cache import Cache
from mlgit.metadata import Metadata
from mlgit.refs import Refs
from mlgit.remote import Remote
from mlgit.index import MultihashIndex, Objects
from mlgit.utils import yaml_load

import os


class Repository(object):
	def __init__(self, config, repotype="dataset"):
		self.__config = config
		self.__repotype = repotype

	'''initializes ml-git repository metadata'''
	def init(self):
		metadatapath = metadata_path(self.__config)
		m = Metadata("", metadatapath, self.__config)
		m.init()

	# TODO: move in utils or something (duplicate)
	def search_spec_file(self, spec):
		repotype = self.__repotype
		try:
			dir = os.sep.join([repotype, spec])
			files = os.listdir(os.sep.join([repotype, spec]))
		except Exception as e: #TODO: search "." path as well
			dir = spec
			files = os.listdir(spec)

		for file in files:
			if spec in file:
				log.debug("search spec file: found [%s]-[%s]" % (dir, file))
				return dir, file

		return None, None

	'''Add dir/files to the ml-git index'''
	def add(self, spec):
		repotype= self.__repotype
		path, file = self.search_spec_file(spec)

		indexpath = index_path(self.__config, repotype)
		metadatapath = metadata_path(self.__config, repotype)

		# Check tag before anything to avoid creating unstable state
		log.info("Repository: check if tag already exists")
		m = Metadata(spec, metadatapath, self.__config, repotype)
		if m.tag_exists(indexpath) == True:
			return None

		# get version of current manifest file
		tag, sha = self.branch(spec)
		manifest=""
		if tag is not None:
			self.checkout(tag)
			m = Metadata(spec, metadatapath, self.__config, repotype)
			md_metadatapath = m.get_metadata_path(tag)
			manifest = os.path.join(md_metadatapath, "MANIFEST.yaml")
			self.checkout("master")

		# adds chunks to ml-git Index
		log.info("Repository %s: adding path [%s] to ml-git index [%s]" % (repotype, path, indexpath))
		idx = MultihashIndex(spec, indexpath)
		idx.add(path, manifest)

		# create hard links in ml-git Cache
		cachepath= cache_path(self.__config, repotype)
		manifest = os.path.join(indexpath, "files", spec, "MANIFEST.yaml")
		c = Cache(cachepath, path, manifest)
		c.update()

	def branch(self, spec):
		repotype = self.__repotype
		refspath = refs_path(self.__config, repotype)
		r = Refs(refspath, spec, repotype)
		return r.head()

	'''prints status of changes in the index and changes not yet tracked or staged'''
	def status(self, spec):
		repotype = self.__repotype
		path, file = self.search_spec_file(spec)

		indexpath = index_path(self.__config)
		metadatapath = metadata_path(self.__config, repotype)

		log.info("Repository %s: status of ml-git index for [%s]" % (repotype, spec))

		# All files in MANIFEST.yaml in the index AND all files in datapath which stats links == 1
		idx = MultihashIndex(spec, indexpath)

		tag, sha = self.branch(spec)
		manifest=""
		if tag is not None:
			self.checkout(tag)
			m = Metadata(spec, metadatapath, self.__config, repotype)
			md_metadatapath = m.get_metadata_path(tag)
			manifest = os.path.join(md_metadatapath, "MANIFEST.yaml")
			self.checkout("master")

		files = idx.get_index()
		print("Changes to be committed")
		for key in files:
			if os.path.exists(os.path.join(path, files[key])) == False:
				print("\tdeleted:\t %s" % (files[key]))
			else:
				print("\tnew file:\t%s" % (files[key]))
			# fs[files] = key

		manifest_files = yaml_load(manifest)
		for k in manifest_files:
			if os.path.exists(os.path.join(path, manifest_files[k])) == False:
				print("\tdeleted:\t %s" % (manifest_files[k]))

		print("\nuntracked files")
		for root, dirs, files in os.walk(path):
			basepath = root[len(path)+1:]
			for file in files:
				fullpath = os.path.join(root, file)
				st = os.stat(fullpath)
				if st.st_nlink <= 1:
					print("\t%s" % (os.path.join(basepath, file)))

	'''commit changes present in the ml-git index to the ml-git repository'''
	def commit(self, spec):
		# Move chunks from index to .ml-git/objects
		repotype = self.__repotype
		indexpath = index_path(self.__config, repotype)
		objectspath = objects_path(self.__config, repotype)
		metadatapath = metadata_path(self.__config, repotype)
		refspath = refs_path(self.__config, repotype)


		# Check tag before anything to avoid creating unstable state
		log.info("Repository: check if tag already exists")
		m = Metadata(spec, metadatapath, self.__config, repotype)
		if m.tag_exists(indexpath) == True:
			return None

		log.debug("%s -> %s" % (indexpath, objectspath))
		# commit objects in index to ml-git objects
		o = Objects(spec, objectspath)
		o.commit_index(indexpath)

		# update metadata spec & README.md
		m = Metadata(spec, metadatapath, self.__config)
		tag, sha = m.commit_metadata(indexpath)

		# update ml-git ref spec HEAD == to new SHA-1 / tag
		if tag is None: return None
		r = Refs(refspath, spec, self.__repotype)
		r.update_head(tag, sha)

		return tag

	'''push all data related to a ml-git repository to the remote git repository and data store'''
	def push(self, spec):
		repotype = self.__repotype
		indexpath = index_path(self.__config, repotype)
		metadatapath = metadata_path(self.__config, repotype)
		objectspath = objects_path(self.__config, repotype)

		idxstore = os.path.join(indexpath, "datastore", "store.dat")

		specpath, specfile = self.search_spec_file(spec)
		fullspecpath = os.path.join(specpath, specfile)

		r = Remote("", self.__config, repotype)
		r.push(idxstore, objectspath, fullspecpath)

		# push metadata spec to remote git repository
		# ensure first we're on master !
		self.checkout("master")
		m = Metadata(spec, metadatapath, self.__config)
		m.push()

	'''Retrieves only the metadata related to a ml-git repository'''
	def update(self):
		repotype = self.__repotype
		metadatapath = metadata_path(self.__config, repotype)
		m = Metadata("", metadatapath, self.__config)
		m.update()

	'''Retrieve only the data related to a specific ML entity version'''
	def fetch(self, tag):
		repotype = self.__repotype
		objectspath = objects_path(self.__config, repotype)
		metadatapath = metadata_path(self.__config, repotype)

		# check if no data left untracked/uncommitted. othrewise, stop.
		r = Remote("", self.__config, repotype)
		r.fetch(objectspath, metadatapath, tag)

	def checkout(self, tag):
		repotype = self.__repotype
		metadatapath = metadata_path(self.__config, repotype)

		# checkout
		m = Metadata("", metadatapath, self.__config)
		m.checkout(tag)

	'''performs fsck on several aspects of ml-git filesystem.
		TODO: add options like following:
		* detect:
			** fast: performs checks on all blobs present in index / objects
			** thorough: perform check on files within cache
		* fix:
		    ** download again corrupted blob
		    ** rebuild cache  
	'''
	def fsck(self):
		repotype = self.__repotype
		objectspath = objects_path(self.__config, repotype)
		indexpath = index_path(self.__config, repotype)

		o = Objects("", objectspath)
		o.fsck()

		idx = MultihashIndex("", indexpath)
		idx.fsck()

	'''Download data from a specific ML entity version into the workspace'''
	def get(self, tag):
		repotype = self.__repotype
		cachepath = cache_path(self.__config, repotype)
		metadatapath = metadata_path(self.__config, repotype)
		objectspath = objects_path(self.__config, repotype)

		self.checkout(tag)
		self.fetch(tag)

		# TODO: check if no data left untracked/uncommitted. otherwise, stop.
		r = Remote("", self.__config, repotype)
		r.get(cachepath, metadatapath, objectspath, tag)

		# restore to master/head
		self.checkout("master")

if __name__ == "__main__":
	from mlgit.config import config_load
	config = config_load()
	r = Repository(config)
	r.init()
	r.add("dataset-ex")
	r.commit("dataset-ex")
	r.status("dataset-ex")
