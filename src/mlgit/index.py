"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.utils import ensure_path_exists, yaml_load, json_load
from mlgit.multihash import check_integrity, create_hashpath, digest
from mlgit import log
import os
import json
import shutil

class Index(object):
	def __init__(self, spec, index_path, hash_based = False):
		self._spec = spec
		self.__init(index_path, hash_based)

	def __init(self, index_path, hash_based):
		self._path = index_path
		self.__hash_based = hash_based

		ensure_path_exists(self._path)
		ensure_path_exists(os.path.join(self._path, "files"))

	def add(self, path, manifestpath):
		if os.path.isdir(path) == True:
			self.add_dir(path, manifestpath)

	def add_dir(self, path):
		pass

	@staticmethod
	def _get_hashpath(path, filename):
		h = filename[:2]
		if h == "Qm": h = filename[2:4]

		return os.path.join(path, h, filename)

	def get_hashpath(self, filename):
		return Index._get_hashpath(self._path, filename)

	def store_chunk(self, filename, data=None):
		hashd = create_hashpath(self._path, filename)
		fullpath = os.path.join(hashd, filename)

		# only valid for hash based filesystem
		if self.__hash_based == True and os.path.isfile(fullpath) == True:
			log.debug("Index: chunk [%s]-[%d] already exists" % (filename, len(data)))
			return False

		if data != None:
			log.info("Index: add chunk [%s]-[%d]" % (filename, len(data)))
			with open(fullpath, 'wb') as f:
				f.write(data)
			return True

	# TODO add : stat to MANIFEST from original file ...
	def update_index(self, filename, objectkey):
		files = self.get_index()
		if objectkey in files:
			log.debug("Index: [%s]-[%s] already in index" % (filename, objectkey))
			return

		dirpath = os.path.join(self._path, "files", self._spec)
		ensure_path_exists(dirpath)
		fullpath = os.path.join(dirpath, "MANIFEST.yaml")
		log.info("Index: add [%s]-[%s] to index manifest" % (filename, objectkey))
		with open(fullpath, "a") as f:
			f.write("%s : %s\n" % (objectkey, filename))

	def update_metadata_store(self, links):
		log.info("Index: update metadata for data store")
		dirpath = os.path.join(self._path, "datastore")
		ensure_path_exists(dirpath)
		fullpath = os.path.join(dirpath, "store.dat")
		with open(fullpath, "a") as f:
			for link in links:
				f.write("%s\n" % (link))

	def reset(self):
		shutil.rmtree(self._path)
		os.mkdir(self._path)

	def get_index(self):
		fullpath = os.path.join(self._path, "files", self._spec, "MANIFEST.yaml")
		try:
			return yaml_load(fullpath)
		except:
			return {}

class Objects(object):
	def __init__(self, spec, objects_path):
		self.__spec = spec
		self._path = objects_path
		ensure_path_exists(objects_path)

	def commit_index(self, index_path):
		self.commit_objects(index_path)

	def commit_objects(self, index_path):
		# Move all chunks from index/ to objects/
		for root, dirs, files in os.walk(index_path):
			dirbase = root[len(index_path):]
			relative_path = root[len(index_path) + 1:]
			if "files" in relative_path: continue
			if "metadata" in relative_path: continue
			if "datastore" in relative_path: continue

			dest_dir = os.path.join(self._path, relative_path)
			if os.path.isdir(dest_dir) == False:
				log.debug("Objects: creating dir %s" % (dest_dir))
				os.makedirs(dest_dir)

			for file in files:
				fullpath = os.path.join(root, file)
				shutil.move(fullpath, os.path.join(dest_dir, file))
				log.info("Objects: commit [%s] to ml-git data store" % (file))

	'''Checks integrity of all files under .mlgit/<repotype>/objects'''
	def fsck(self):
		corruption_found = False
		log.info("Objects: starting integrity check on [%s]" % (self._path))
		for root, dirs, files in os.walk(self._path):
			if "files" in root: continue

			for file in files:
				fullpath = os.path.join(root, file)
				with open(fullpath, 'rb') as c:
					while True:
						d = c.read(256 * 1024)
						if not d: break
						if check_integrity(file, d) == False:
							corruption_found = True
		return corruption_found


class MultihashIndex(Index):
	def __init__(self, spec, index_path):
		super(MultihashIndex, self).__init__(spec, index_path, hash_based = True)

	def add_dir(self, dirpath, manifestpath):
		self.manifestfiles = yaml_load(manifestpath)

		for root, dirs, files in os.walk(dirpath):
			if "." == root[0]: continue

			basepath = root[:len(dirpath)+1:]
			relativepath = root[len(dirpath)+1:]
			for file in files:
				filepath = os.path.join(relativepath, file)
				if (".spec" in file) or ("README.md" == file): self.add_metadata(basepath, filepath)
				else: self.add_file(basepath, filepath)

	def add_metadata(self, basepath, filepath):
		log.info("Multihash: add file [%s] to ml-git index [%s]" % (filepath, self._path))
		fullpath = os.path.join(basepath, filepath)

		metadatapath = os.path.join(self._path, "metadata", self._spec)
		ensure_path_exists(metadatapath)

		dstpath = os.path.join(metadatapath, filepath)
		if os.path.exists(dstpath) == False:
			os.link(fullpath, dstpath)

	def add_file(self, basepath, filepath):
		fullpath = os.path.join(basepath, filepath)

		st = os.stat(fullpath)
		if st.st_nlink > 1:
			log.debug("Multihash: file [%s] already exists in ml-git repository" % (filepath))
			return

		log.info("Multihash: add file [%s] to ml-git index [%s]" % (filepath, self._path))
		links = []

		with open(fullpath, 'rb') as f:
			while True:
				d = f.read(256*1024)
				if d:
					scid = digest(d)
					self.store_chunk(scid, d)
					links.append( {"Hash" : scid, "Size": len(d)} )
				else:
					break

		ls = json.dumps({ "Links" : links })
		scid = digest(ls.encode())

		if scid in self.manifestfiles:
			# TODO: add metadata about that file to filter out quickly (no digest at each add) and for usage status (not show in untracked)
			log.info("Index: file [%s] duplicate in ml-git repository of [%s]. filtering out." % (filepath, self.manifestfiles[scid]))
			return

		self.store_chunk(scid, ls.encode())
		self.update_index(filepath, scid)

		hs = [scid]
		for link in links:
			hs.append(link["Hash"])
		self.update_metadata_store(hs)


	def _get_file(self, objectkey, path, file):
		# Get all file chunks definition
		jl = json_load(self.get_hashpath(objectkey))
		if check_integrity(objectkey, json.dumps(jl).encode()) == False:
			return

		# write all chunks into temp file
		log.info("Index: getting file [%s] from local index" % (file))
		dirs = os.path.dirname(file)
		base = os.path.basename(file)

		fulldir = os.path.join(path, dirs)
		if dirs != '' and os.path.isdir(fulldir) == False:
			log.info("Index: creating dir %s " % (fulldir))
			os.makedirs(fulldir)

		with open(os.path.join(path, file), 'wb') as f:
			for chunk in jl["Links"]:
				h = chunk["Hash"]
				s = chunk["Size"]
				log.debug("Index: cat content of [%s]-[%d] to [%s]" % (h, s, file))
				with open(self.get_hashpath(h), 'rb') as c:
					while True:
						d = c.read(256 * 1024)
						if not d: break
						if check_integrity(h, d) == False:
							return
						f.write(d)

	def get(self, objectkey, destination="/tmp/ml-git-tmp"):
		files = self.get_index()
		try:
			file = files[objectkey]
		except:
			log.error("Index: [%s] not found in local object store" % (objectkey))

		return self._get_file(objectkey, destination, file)

	'''Checks integrity of all files under .mlgit/<repotype>/objects'''

	def fsck(self):
		corruption_found = False
		log.info("Objects: starting integrity check on [%s]" % (self._path))
		for root, dirs, files in os.walk(self._path):
			if "files" in root: continue
			if "metadata" in root: continue
			if "datastore" in root: continue

			for file in files:
				fullpath = os.path.join(root, file)
				with open(fullpath, 'rb') as c:
					while True:
						d = c.read(256 * 1024)
						if not d: break
						if check_integrity(file, d) == False:
							corruption_found = True
		return corruption_found

class FileIndex(object):
	def add(self, filepath):
		pass

if __name__=="__main__":
	from mlgit.log import init_logger
	init_logger()
	m = MultihashIndex("/tmp/mh_index")
	m.add("data")
	# m.add("image.jpg")
	m.get("QmRm1HtbBa5RUEuPXT1dFyyDKJo5KC1yiyASRQPNsfSuDn")
	# m.reset()
	o = Objects("/tmp/mh_objects")
	o.move_from_index("/tmp/mh_index")
