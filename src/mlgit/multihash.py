"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit import log
from cid import CIDv0, make_cid
import multihash
import hashlib
import errno
import os

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


