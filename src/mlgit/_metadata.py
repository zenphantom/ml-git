"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from mlgit.utils import ensure_path_exists, yaml_save, yaml_load
from mlgit import log
from git import Repo, Git
import os
import yaml

class MetadataRepo(object):
	def __init__(self, git, path):
		self.__path = path
		self.__git = git
		ensure_path_exists(self.__path)

	def init(self):
		log.info("metadata init: [%s] @ [%s]" % (self.__git, self.__path))
		Repo.clone_from(self.__git, self.__path)

	def check_exists(self):
		log.info("metadata check existence [%s] @ [%s]" % (self.__git, self.__path))
		try:
			r = Repo(self.__path)
		except:
			return False
		return True

	def checkout(self, sha):
		r = Git(self.__path)
		r.checkout(sha)

	def update(self):
		log.info("Metadata Manager pull [%s]" % (self.__path))
		r = Repo(self.__path)
		o = r.remotes.origin
		r = o.pull()

	def commit(self, file, msg):
		log.info("commit : repo[%s] --- spec[%s]" % (self.__path, file))
		r = Repo(self.__path)
		r.index.add([file])
		r.index.commit(msg)

	def tag_add(self, tag):
		r = Repo(self.__path)
		return r.create_tag(tag, message='Automatic tag "{0}"'.format(tag))

	def publish(self):
		log.info("Metadata Manager push [%s]" % (self.__path))
		r = Repo(self.__path)
		r.remotes.origin.push(tags=True)
		r.remotes.origin.push()

	def tag_exists(self, tag):
		tags= []
		r = Repo(self.__path)
		if tag in r.tags:
			tags.append(tag)

		model_tag = "__".join( tag.split("__")[-3:] )
		for rtag in r.tags:
			if model_tag in str(rtag):
				tags.append(str(rtag))

		return tags

	def __realname(self, path, root=None):
		if root is not None:
			path=os.path.join(root, path)
		result=os.path.basename(path)
		return result

	def list(self, title="ML Models"):
		metadata_path = self.__path

		prefix=0
		if metadata_path != '/':
			if metadata_path.endswith('/'): metadata_path=metadata_path[:-1]
			prefix=len(metadata_path)

		print(title)
		for root, dirs, files in os.walk(metadata_path):
			if root == metadata_path: continue
			if ".git" in root: continue

			level = root[prefix:].count(os.sep)
			indent=subindent =''
			if level > 0:
				indent = '|   ' * (level-1) + '|-- '
			subindent = '|   ' * (level) + '|-- '
			print('{}{}'.format(indent, self.__realname(root)))
			# print dir only if symbolic link; otherwise, will be printed as root
			for d in dirs:
				if os.path.islink(os.path.join(root, d)):
					print('{}{}'.format(subindent, self.__realname(d, root=root)))
			for f in files:
				if "README" in f: continue
				print('{}{}'.format(subindent, self.__realname(f, root=root)))

	def metadata_spec_from_name(self, spec_name):
		specs = []
		for root, dirs, files in os.walk(self.__path):
			if ".git" in root: continue
			for file in files:
				if spec_name in os.path.join(root, file):
					specs.append( (root, file))
		return specs

	def metadata_print(self, metadata_file, spec_name):
		md = yaml_load(metadata_file)

		sections = ["dataset", "model", "metadata"]
		for section in sections:
			if section in [ "model", "dataset" ]:
				try:
					md[section] # "hack" to ensure we don't print something useless
					# "dataset" not present in "model" and vice versa
					print("-- %s : %s --" % (section, spec_name))
				except:
					continue
			elif section not in [ "model", "dataset" ]:
				print("-- %s --" % (section))
			try:
				print(yaml.dump(md[section]))
			except:
				continue

	def sha_from_tag(self, tag):
		try:
			r = Repo(self.__path)
			return r.git.rev_list(tag).split("\n", 1)[0]
		except:
			return None

	def show(self, spec_name):
		specs = self.metadata_spec_from_name(spec_name)
		for path, file in specs:
			self.metadata_print(os.path.join(path, file), file)

	def get(self, categories, model_name, file=None):
		if file is None:
			full_path = os.path.join(self.__path, os.sep.join(categories), model_name, model_name)
		else:
			full_path = os.path.join(self.__path, os.sep.join(categories), model_name, file)
		log.info("metadata GET: %s" % (full_path))
		if os.path.exists(full_path):
			return yaml_load(full_path)
		return None

	def __get_categories_spec_from_tag(tag):
		sp = tag.split("__")
		return sp[:-2], sp[-2:-1][0]


class MetadataManager(MetadataRepo):
	def __init__(self, config, type="model"):
		store = type
		#log.info("metadatamanager: %s" % (config))
		self.path = config[type]["metadata"]
		self.git =  config[type]["git"]
		self.data = config[type]["data"]

		super(MetadataManager, self).__init__(self.git, self.path)

class MetadataObject(object):
	def __init__(self):
		pass

if __name__=="__main__":
	r = MetadataRepo("ssh://git@github.com/standel/ml-datasets", "ml-git/datasets/")
	tag = "vision-computing__images__cifar-10__1"
	sha = "0e4649ad0b5fa48875cdfc2ea43366dc06b3584e"
	#r.checkout(sha)
	#r.checkout("master")
	print(get_from_tag(tag))