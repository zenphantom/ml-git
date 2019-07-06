"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.hashfs import HashFS
import unittest
import tempfile
import os
import hashlib

data = "blabla"

chunks256 = {
	"QmXhKe1k6v79t4GFj63WCg1Gh3kMJ8oDe1mXmWLkRSLNHG",
	"QmQr6PX9VfiFqMVEojUFr3354spuD8PFkSTa6nFFMgir6y",
	"Qmf4s7bNVBTKYbPXMg8CMzpwvbwwYMnL5kDx91AAndoLqa",
	"QmZ1Z8qsPPHra9TS76XSqZ8EPj7Fy1fCzkhrFgsBP2nBDe",
	"QmbDDdYepSRVE6FUDGVnD7UG1kftvF7ZTohysuLjTXVRt5",
	"QmTwXrBVLpTb3B6YcFK7gevSMqyQDJNtvyaoCgbJZipoJZ",
	"QmWk4PruP7fV1CkeUcguYaWhL9tGwfKoZ91X2yKGjEyYJx",
	"QmT2feNX8nrvbXtCGqh58XKpSeJ8jMqqZkHWRqxCjT3hxd",
	"QmSsSqemrdGmahBdvWUNBQ4LH7prfB3mAQeKoCfiYLGwfT",
	"QmaEB9yCGm7YuNwgPWL52Ecw3vdzE9UUzoPbQfqE1ixthd",
	"QmX1CD51C8ZUbFjnudReAaYmUrP84o6AazLmQLSuxGUBcG",
	"QmYxncm2xyXSYVwaqQpyYYE42cSbMnZVBV8dcwbJwHHaYm",
	"QmTcDtqE3pnhHaHKNvdsgEk7YT3mfA8sR7876HYMDifche",
	"QmZzBL9hstuCxV7Hqr8TsEh9Pj1C1tWqTou4UX7kRL5gQ1",
	"QmWrabtWWtF6baeQ2y7AXrWhhnGXHgphenUDWPVic1jiJC",
	"QmNq5iJLFScU4hyiKHyqw5vSQFeXT4Yrn1HLtFPmmMPmB3",
	"QmbPottLyPqUZgzq4ZwWbTiW3y5sPistwjwinKdmnD4g57",
	"QmPC1RQtM2oXvhUfSnadV48t3ZPf942p4WtP6rb4mPv2yA",
	"QmQ1JVnpVkS87GrGRWA1ux5qHGpyQiF5jjYwePPyy2PGyP",
	"QmcjrCotLC84f1rMCrNkWuVTMqFA37aeSc9VN8W3tcru8p",
	"QmWEmfjMgf6PcPVjU7WRCroQ4w8bXBz7q7KgK9vJ3gWAD7",
	"QmYWd3aDNRA5E3VAZ7WhG4Buqtfw6wa44J6iaHFTNYs7hT"
}
chunks1024 = {
	"QmTP8Rz799FL9aznMQuQRMpeMnKSKbm9LbCfpDpCM5Y2Gz",
	"QmSs5TZmMZjLYH9SYRMRuxZZ64LaeK3Z2EWxj7t5EfZCEG",
	"QmRVGu9zHpCHpa21BnTAgTNQyqWPkfxYJAjpiVV6Az9GQR",
	"QmSGJHrLN46z9yjMamgaMhiNBQb4vqsB9NiNG3u7SXJkSq",
	"QmQif6N4AezdiQScthYUEntuacz26YFvWR5qunRnPVVBWz",
	"QmWEmfjMgf6PcPVjU7WRCroQ4w8bXBz7q7KgK9vJ3gWAD7",
	"QmfK44DZ2gtpEXMPoSna54wQb3zjo1V51iqRh6Nb33WXLa"
}

def md5sum(file):
	hash_md5 = hashlib.md5()
	with open(file, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	return hash_md5.hexdigest()

class S3StoreTestCases(unittest.TestCase):
	def test_put256K(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			print(tmpdir)
			hfs_path = os.path.join(tmpdir, "hashfs")
			os.mkdir(hfs_path)
			hfs = HashFS(hfs_path, blocksize=256*1024)
			hfs.put("data/think-hires.jpg")
			for root, dirs, files in os.walk(hfs_path):
				for file in files:
					self.assertTrue(file in chunks256)

	def test_put1024K(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			print(tmpdir)
			hfs_path = os.path.join(tmpdir, "hashfs")
			os.mkdir(hfs_path)
			hfs = HashFS(hfs_path, blocksize=1024*1024)
			hfs.put("data/think-hires.jpg")
			for root, dirs, files in os.walk(hfs_path):
				for file in files:
					self.assertTrue(file in chunks1024)

	def test_get_simple(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			original_file = "data/think-hires.jpg"
			dst_file = os.path.join(tmpdir, "think-hires.jpg")
			hfs_path = os.path.join(tmpdir, "hashfs")
			os.mkdir(hfs_path)
			hfs = HashFS(hfs_path, blocksize=1024*1024)
			objkey = hfs.put(original_file)
			hfs.get(objkey, dst_file)
			self.assertEqual(md5sum(original_file), md5sum(dst_file))

	def test_corruption(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			original_file = "data/think-hires.jpg"
			dst_file = os.path.join(tmpdir, "think-hires.jpg")
			hfs_path = os.path.join(tmpdir, "hashfs")
			os.mkdir(hfs_path)
			hfs = HashFS(hfs_path, blocksize=1024*1024)
			objkey = hfs.put(original_file)
			chunk = os.path.join(hfs_path, "TP", "QmTP8Rz799FL9aznMQuQRMpeMnKSKbm9LbCfpDpCM5Y2Gz")
			with open(chunk, "wb") as f:
				f.write(b"blabla")
			self.assertFalse(hfs.get(objkey, dst_file))
			self.assertTrue(os.path.exists(dst_file) == False)

if __name__ == "__main__":
	unittest.main()