"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

#!/usr/bin/env python3

from mlgit.config import config_load, list_repos
from mlgit.log import init_logger
from mlgit.labels_manager import LabelsManager
from mlgit.options import parsed_options

if __name__=="__main__":
	config = config_load()
	init_logger()

	args = parsed_options("labels")

	if args.cmd == "add":
		metadata_spec = args.label
		m = LabelsManager(config)
		m.store(metadata_spec)
	if args.cmd == "get":
		metadata_spec = args.label
		repo = args.repository
		m = LabelsManager(config)
		m.get(metadata_spec)
	#elif arg1 == "search":
	if args.cmd == "list":
		m = LabelsManager(config)
		m.list()
	if args.cmd == "show":
		metadata_spec = args.label
		m = LabelsManager(config)
		m.show(metadata_spec)
	if args.cmd == "publish":
		m = LabelsManager(config)
		m.publish()
	if args.cmd == "update":
		repo = args.repository
		m = LabelsManager(config)
		m.update()