"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.hashfs import MultihashFS
import unittest
import tempfile
import os
import hashlib

chunks256 = {
	"zdj7Wena1SoxPakkmaBTq1853qqKFwo1gDMWLB4SJjREsuGTC",
	"zdj7WXwLkxDM9Bri4oAYURsiQsdh62LvfoPcks6madvB8HkGu",
	"zdj7WnA7V2SLevvRJhT6R5pENfWYp9PFuCTx4dUooYqc5NF1W",
	"zdj7Wg6oWGwErmTSrmMqqV4hvxo1wJhgZ5Ls57NvVFrCUM5Pa",
	"zdj7WiJTzyifuu66oZPx1TQ5VJpdxsLdnXhL87WYhjQGy4L41",
	"zdj7Wb2nDcZCHwButQULzGjZ2kzz4Aqvqo2oHzKsUyyPAPhUV",
	"zdj7WdqJmHyEb95sv4aDMeXQxMFxN5ifCjwRTR3hmhwYgYSUt",
	"zdj7Wa7v1oazGLXUFC81aegzuAP4rVaSuFyS4h36eLsYtcc8Z",
	"zdj7WZxhD5qi6kNTQVZfFRz3mttuL2JNiTu2j3rU14PMmqqqP",
	"zdj7WhKRXQG8Eb9n6Fc8FHgtcTVg8qRwgtcs7o85UDtqAXnsZ",
	"zdj7We6SaW53c35Ty3ieNPG2xPL74aZnLWJTJkJ58qami35nC",
	"zdj7Wg42zC6pT13RDFWa9nbQv4cepe35Kyd3oYAHjyykirUih",
	"zdj7WahUGGHuJGJAHbF7fbVYcagAfFDNhZ1HRXdm5w23AEWsa",
	"zdj7Wh5RhamjNNoqCRDab65jcXi1wCdjRvyL8Jb9KWREmeaZw",
	"zdj7WdwpyKaNMihUHxKmi4nQEMGKzTy1EEqX6skBBtPRTJcU8",
	"zdj7WVvL5jQ6v64wRHe42wToTm12TqyAbxzeKgsZ3nSanxfLy",
	"zdj7WiV4GKQpsK5SQJkoJu8TqZ4gBHK7GJ2p4MFT82SbedaF3",
	"zdj7WWHFnqxCWH8oQnbBXYFMRySfmb6rbSwvqHumeyjaqUw96",
	"zdj7WX6YsDtMDuiyzACAF7dnKvPuV2R8FfDc3xUKBnenTxB9K",
	"zdj7Wjq6aExBfbfXjAGwbLNPHL1z3SbkeznJvZ22vtii4RoJk",
	"zdj7WdL23ARY8ZzV6ofCrU35Edxh9L3EjQFhRjCyxJxs854P3",
	"zdj7WgHSKJkoJST5GWGgS53ARqV7oqMGYVvWzEWku3MBfnQ9u"
}
chunks1024 = {
	"zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv",
	"zdj7WZxKpzqD3CwQzTNHAK3nLQ7iGY2MrTgtYvVPvGk4786QC",
	"zdj7WYaXGb49HfthHKvvXQnYqCyc3hqUDNgAV9MPHskzRiAaM",
	"zdj7WZMYfHQDXab2h3HKWeCE5YvocnWePHK1h7tvrHnFxsecm",
	"zdj7WXouTo828UEb7kYdSW67AjUCqBTp5g4NjVNaapTCw45gv",
	"zdj7WdL23ARY8ZzV6ofCrU35Edxh9L3EjQFhRjCyxJxs854P3",
	"zdj7WYm6eMEr9XmaWYKj45fmaBRXsYCWQe21K5yM6HnWrDTsR"
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
			hfs = MultihashFS(tmpdir, blocksize=256*1024)
			hfs.put("data/think-hires.jpg")
			for files in hfs.walk():
				for file in files:
					self.assertTrue(file in chunks256)

	def test_put1024K(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			print(tmpdir)
			hfs = MultihashFS(tmpdir, blocksize=1024*1024)
			hfs.put("data/think-hires.jpg")
			for files in hfs.walk():
				for file in files:
					self.assertTrue(file in chunks1024)

	def test_get_simple(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			original_file = "data/think-hires.jpg"
			dst_file = os.path.join(tmpdir, "think-hires.jpg")
			hfs = MultihashFS(tmpdir, blocksize=1024*1024)
			objkey = hfs.put(original_file)
			hfs.get(objkey, dst_file)
			self.assertEqual(md5sum(original_file), md5sum(dst_file))

	def test_corruption(self):
		with tempfile.TemporaryDirectory() as tmpdir:
			original_file = "data/think-hires.jpg"
			dst_file = os.path.join(tmpdir, "think-hires.jpg")
			hfs = MultihashFS(tmpdir, blocksize=1024*1024)
			objkey = hfs.put(original_file)
			chunk = os.path.join(tmpdir, "hashfs", "aU", "No", "zdj7WaUNoRAzciw2JJi69s2HjfCyzWt39BHCucCV2CsAX6vSv")
			with open(chunk, "wb") as f:
				f.write(b"blabla")
			self.assertFalse(hfs.get(objkey, dst_file))
			self.assertTrue(os.path.exists(dst_file) == False)

if __name__ == "__main__":
	unittest.main()