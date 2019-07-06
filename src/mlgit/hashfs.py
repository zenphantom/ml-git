"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log
from mlgit.utils import json_load
from cid import CIDv0, make_cid
import multihash
import hashlib
import errno
import os
import json

'''Implementation of a content-addressable filesystem
This filesystem guarantees by design:
* immutability of any file in the filesystem
* 
'''
class HashFS(object):
	def __init__(self, path, blocksize = 256*1024):
		self._path = path
		self._blk_size = blocksize

	def _get_hash(self, filename):
		h = filename[:2]
		if h == "Qm": h = filename[2:4]
		return h

	def _get_hashpath(self, filename):
		h = self._get_hash(filename)
		return os.path.join(self._path  , h, filename)

	def create_hashpath(self, filename):
		h = self._get_hash(filename)
		hashd = os.path.join(self._path, h)
		try:
			os.mkdir(hashd)
		except OSError as exc:
			if exc.errno != errno.EEXIST:
				raise
			pass
		return hashd

	def _store_chunk(self, filename, data):
		hashd = self.create_hashpath(filename)
		fullpath = os.path.join(hashd, filename)

		if os.path.isfile(fullpath) == True:
			log.debug("HashFS: chunk [%s]-[%d] already exists" % (filename, len(data)))
			return False

		if data != None:
			log.info("HashFS: add chunk [%s]-[%d]" % (filename, len(data)))
			with open(fullpath, 'wb') as f:
				f.write(data)
			return True

	def _check_integrity(self, cid, data):
		cid0 = self._digest(data)
		if cid == cid0:
			log.debug("HashFS: checksum verified for chunk [%s]" % (cid))
			return True
		log.error("HashFS: corruption detected for chunk [%s] - got [%s]" % (cid, cid0))
		return False

	def _digest(self, data):
		m = hashlib.sha256()
		m.update(data)
		h = m.hexdigest()
		mh = multihash.encode(bytes.fromhex(h), 'sha2-256')
		cid = CIDv0(mh)
		return str(cid)

	def put(self, srcfile):
		links = []
		with open(srcfile, 'rb') as f:
			while True:
				d = f.read(self._blk_size)
				if d:
					scid = self._digest(d)
					self._store_chunk(scid, d)
					links.append( {"Hash" : scid, "Size": len(d)} )
				else:
					break

		ls = json.dumps({ "Links" : links })
		scid = self._digest(ls.encode())
		self._store_chunk(scid, ls.encode())
		return scid

	def get(self, objectkey, dstfile):
		size = 0

		# Get all file chunks definition
		jl = json_load(self._get_hashpath(objectkey))
		if check_integrity(objectkey, json.dumps(jl).encode()) == False:
			return size

		corruption_found = False
		# concat all chunks to dstfile
		with open(dstfile, 'wb') as f:
			for chunk in jl["Links"]:
				h = chunk["Hash"]
				s = chunk["Size"]
				log.debug("HashFS: get chunk [%s]-[%d]" % (h, s))
				size += int(s)
				with open(self._get_hashpath(h), 'rb') as c:
					while True:
						d = c.read(self._blk_size)
						if not d: break
						if self._check_integrity(h, d) == False:
							corruption_found = True
							break
						f.write(d)
				if corruption_found == True: break

		if corruption_found == True:
			size = 0
			os.unlink(dstfile)
		return size

	def _update_metadata_store(self, links):
		log.info("HashFS: update metadata for data store")
		dirpath = os.path.join(self._path, "datastore")
		ensure_path_exists(dirpath)
		fullpath = os.path.join(dirpath, "store.dat")
		with open(fullpath, "a") as f:
			for link in links:
				f.write("%s\n" % (link))

def digest(data):
	m = hashlib.sha256()
	m.update(data)
	h = m.hexdigest()
	mh = multihash.encode(bytes.fromhex(h), 'sha2-256')
	cid = CIDv0(mh)
	return str(cid)

def check_integrity(cid, data):
	cid0 = digest(data)
	if cid == cid0:
		log.debug("multihash: checksum verified for chunk [%s]" % (cid))
		return True
	log.error("multihash: corruption detected for chunk [%s] - got [%s]" % (cid, cid0))
	return False

def create_hashpath(path, filename):
	h = filename[:2]
	if h == "Qm": h = filename[2:4]
	hashd = os.path.join(path, h)
	try:
		os.mkdir(hashd)
	except OSError as exc:
		if exc.errno != errno.EEXIST:
			raise
		pass
	return hashd

if __name__=="__main__":
	try:
		os.mkdir("/tmp/hashfs-test")
	except:
		pass
	hfs = HashFS("/tmp/hashfs-test/")
	scid = hfs.write("think-hires.jpg")
	print("wrote %s" % (scid))
	hfs.get(scid, "think-hires-copy.jpg")



