"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

#!/usr/bin/env python3

from mlgit.config import config_load, list_repos, repo_config
from mlgit.log import init_logger
from mlgit.admin import init_mlgit, init_repos, show_config
import argparse

reponame_option = {"repository":
    {
        "help": "name of the ml-git repository to create"
    }
}
command_usage = {
    "--init": {
        "help": '''initializes an instance of ml-git repository''',
        "action": 'store_true',
        # "default" : ""
        # "type" :
        "subs": lambda: dict(reponame_option)
    },
    "--init-metadata": {
        "help": '''initializes the metadata repositories''',
        "action": 'store_true',
    },
    "--list": {
        "help": '''list all available ML repositories''',
    },
    "--show": {
        "help": ''''shows details about the services running''',
    },
    "--start": {
        "help": '''start the execution of Machine Learning Datasets & Models services''',
    },
    "--stop": {
        "help": '''stop the execution of Machine Learning Datasets & Models services''',
    },
    "--up": {
        "help": '''create and start Machine Learning Datasets & Models services''',
    },
    "--down": {
        "help": '''stop and remove Machine Learning Datasets & Models services''',
    },
}

if __name__ == "__main__":
    config_load()
    init_logger()

    parser = argparse.ArgumentParser()
    first_level_command = parser.add_mutually_exclusive_group(required=True)
    for cmd, spec in command_usage.items():
        help = spec["help"]
        first_level_command.add_argument(cmd, help=help, action='store_true')
    args = parser.parse_args()

    if args.init:
        print("initializing ...")
        init_mlgit()
    if args.init_metadata:
        print("initializing metadata...")
        init_repos()
    if args.list:
        print("ml-git repositories:")
        for repo in list_repos():
            print("\t%s" % (repo))
    if args.show:
        show_config()

    # TODO: start / stop docker services for IPFS
    # if args.cmd == "start":
    # if args.cmd == "stop":
    # if args.cmd == "up":
    # if args.cmd == "down":
