"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

#!/usr/bin/env python3

from mlgit.config import config_load, list_repos
from mlgit.log import init_logger
from mlgit.dataset_manager import DatasetManager
from mlgit.options import parsed_options
from mlgit.repository import Repository

if __name__=="__main__":
	config = config_load()
	init_logger()

	args = parsed_options("dataset")

	repotype = "dataset"

	if args.cmd in ["init", "update", "fsck"]:
		r = Repository(config, repotype)
		if args.cmd == "init": r.init()
		elif args.cmd == "update": r.update()
		elif args.cmd == "fsck": r.fsck()

	if args.cmd in [ "add", "commit", "status", "push", "get", "fetch"]:
		spec = args.spec
		r = Repository(config, repotype)

		if args.cmd == "add": r.add(spec)
		elif args.cmd == "commit": r.commit(spec)
		elif args.cmd == "status": r.status(spec)
		elif args.cmd == "push": r.push(spec)
		elif args.cmd == "get": r.get(spec)
		elif args.cmd == "fetch": r.fetch(spec)


	if args.cmd == "list":
		m = DatasetManager(config)
		m.list()

	if args.cmd == "show":
		dataset_name = args.dataset
		repo = args.repository
		repos = [repo]
		if repo == "all":
			repos = list_repos()
		print(repos)
		for repo in repos:
			print("*** %s ***" % (config))
			m = DatasetManager(config)
			m.show(dataset_name)
			print


