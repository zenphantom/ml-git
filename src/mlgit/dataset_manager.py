"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.config import get_key
from mlgit.utils import ensure_path_exists, yaml_save, yaml_load
from mlgit._metadata import MetadataManager
from mlgit import log
from mlgit.store import store_factory
import os
from pprint import pprint

class DatasetManager(MetadataManager):
	def __init__(self, config, dryrun=False):
		self.__dryrun = dryrun
		self.config = config
		self.__mgr_type = "dataset"
		super(DatasetManager, self).__init__(config, "dataset")

	def __dataset_get(self, categories, spec):
		metadata = self.get(categories, spec)
		if metadata is None: return None

		mgr_type = self.__mgr_type
		version = metadata[mgr_type]["version"]

		manifest = metadata[mgr_type]["manifest"]
		store = store_factory(self.config, manifest["store"])

		data_path = os.sep.join([os.sep.join(categories), spec, str(version)])
		full_path = os.path.join(self.config[mgr_type]["data"], data_path)
		ensure_path_exists(full_path)

		for part in manifest["files"]: # MANIFEST files => read files from there
			log.debug("S3 Store: manifest part [%s]" % (part))
			files = self.get(categories, spec, part)
			for kv in files:
				for k, v in kv.items():
					log.debug("S3 Store: file [%s] ; key [%s]" % (k, v))
					filepath = os.sep.join([full_path, k])
					#don't download file if already local
					if os.path.exists(filepath) == True:
						# TODO: check existence in previous versions if any
						# TODO: check cksum to ensure integrity
						log.info("S3 Store: [%s] already in the local store [%s]" % (k, data_path))
						continue
					store.get(filepath, v)
			#TODO: convert to shutil.copy2 to preserve file metadata?
			yaml_save(files, os.path.join(full_path, os.path.basename(part)))
		yaml_save(metadata, os.path.join(full_path, os.path.basename(spec)))

	def dataset_get(self, spec):
		try:
			splits = spec.split(':')
		except:
			splits = spec.split(os.sep)
		cats = splits[:-1]
		spec = splits[-1]
		self.__dataset_get(cats, spec)

	def search_spec_file(self, spec):
		mgr_type = self.__mgr_type
		try:
			dir = os.sep.join([mgr_type, spec])
			files = os.listdir(os.sep.join([mgr_type, spec]))
		except Exception as e: #TODO: search "." path as well
			dir = spec
			files = os.listdir(spec)

		for file in files:
			if spec in file:
				log.debug("search spec file: found [%s]-[%s]" % (dir, file))
				return dir, file

		return None, None

	def dataset_store(self, spec):
		mgr_type = self.__mgr_type
		dir, specfile = self.search_spec_file(spec)
		if dir is None: return

		specfile_path = os.sep.join([dir, specfile])
		metadata = yaml_load(specfile_path)
		prefix = self.dataset_path(metadata)

		manifest = metadata[mgr_type]["manifest"]
		store = store_factory(self.config, manifest["store"])

		for manifest in manifest["files"]:
			files = []
			manifestfile_path = os.sep.join([dir, manifest])
			ymanifest = yaml_load(manifestfile_path)

			for file in ymanifest:
				for k, v in file.items():
					#TODO append dataset_metadata_path
					#subdir, ls = store.store(k, v, path=dir, prefix=prefix)
					ls = store.store(k, v, path=dir, prefix=prefix)
					files.extend( ls )
					#files.extend( (k, v) )
					file_path = os.sep.join([dir, v])
					log.debug("Metadata Manager store: file [%s] exists: [%s]" % (file_path, os.path.exists(file_path)))
			#save files with metadata from store
			self.__manifest_store(prefix, manifest, files)

		#saves README.md if any
		self.__readme_store(dir, prefix)

		#saves metadata and commit
		self.__dataset_store(prefix, metadata[mgr_type]["name"], metadata)

	def __readme_store(self, path, prefix):
		import shutil
		readme = "README.md"
		readme_path = os.sep.join([path, readme])

		if os.path.exists(readme_path) == False: return

		full_path = os.sep.join([self.path, prefix])
		readme_prefix = os.sep.join([full_path, readme])
		return shutil.copy2(readme_path, readme_prefix)


	def __manifest_store(self, prefix, manifest_name, manifest):
		full_path = os.sep.join([self.path, prefix])
		log.info("S3 Store: saving manifest [%s] in [%s]" % (manifest_name, full_path))

		if get_key("auto_create_category") == True:
			log.debug("creating category: %s" % (full_path))
			ensure_path_exists(full_path)

		manifest_path = os.sep.join([full_path, manifest_name])
		yaml_save(manifest, manifest_path)

	def __dataset_store(self, prefix, metadata_file, metadata):
		full_path = os.sep.join([self.path, prefix])

		#auto-create categories directory structure
		if get_key("auto_create_category") == True:
			log.debug("creating category: %s" % (full_path))
			ensure_path_exists(full_path)

		#saves yaml metadata specification
		metadata_path = os.sep.join([full_path, metadata_file])
		yaml_save(metadata, metadata_path)

		#generates a tag to associate to the commit
		tag = self.dataset_tag(metadata)
		log.info("S3 Store : tag [%s] generated" % (tag))

		#check if tag already exists in the ml-git repository
		tags = self.tag_exists(tag)
		if len(tags) > 0:
			log.error("S3 Store: tag [%s] already exists in the ml-git repository" % (tag))
			for t in tags: log.error("\t%s" %(t))
			return False

		#generates a commit message
		msg = self.dataset_message(metadata)
		log.info("S3 Store: commit message [%s]" % (msg))

		self.commit(prefix, msg)
		self.tag_add(tag)

		return True

	def __dataset_spec(self, metadata, sep):
		mgr_type = self.__mgr_type
		cats =  metadata[mgr_type]["categories"]
		if type(cats) is list:
			categories = sep.join(cats)
		else:
			categories = cats

		# Generate Spec from Dataset Name & Categories
		return sep.join([ categories, metadata[mgr_type]["name"] ])

	def dataset_tag(self, metadata):
		mgr_type = self.__mgr_type

		sep = "__"
		tag = self.__dataset_spec(metadata, sep)

		## add Version
		tag = sep.join( [ tag, str(metadata[mgr_type]["version"]) ] )

		log.debug("metadata [%s] tag [%s]" % (mgr_type, tag))
		return tag

	def dataset_path(self, metadata):
		sep = os.sep
		path = self.__dataset_spec(metadata, sep)
		log.debug("metadata dataset path: %s" % (path))
		return path

	def dataset_message(self, metadata):
		mgr_type = self.__mgr_type
		message = self.dataset_path(metadata)
		try:
			message = message + " - " + metadata[mgr_type]["date"]
		except:
			pass
		try:
			message = message + "\n\n" + metadata["metadata"]["description"]
		except:
			pass

		return message
