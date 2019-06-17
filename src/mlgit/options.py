"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import argparse

repo_option = {"--repository":
    {
        "help": "specify ml repository [default: global]",
        "default": "global",
    }
}
model_option = {"model":
    {
        "help": "model name specification"
    }
}
force_option = {"--force":
    {
        "help": "force command to execute [default: False]",
        "default": False,
    }
}
dataset_option = {"dataset":
    {
        "help": "dataset name specification"
    }
}
label_option = {"label":
    {
        "help": "label name specification"
    }
}
reponame_option = {"repository":
    {
        "help": "name of the ml-git repository to create"
    }
}

command_usage1 = {
    "update": {
        "help": '''updates machine learning models metadata available''',
        "subs": lambda: repo_option,
    },
    "list": {
        "help": '''lists models stored in mlgit distributed storage''',
        "subs": lambda: repo_option,
    },
    "publish": {
        "help": '''publishes added datasets/models''',
        "subs": lambda: repo_option,
    }
}

force_option.update(model_option)
additional_options = force_option
command_usage = {
    "add": {
        "help": '''adds a new model under management of ml-git''',
        "subs": lambda: dict(repo_option, **additional_options),
    },
    "get": {
        "help": '''gets a model from mlgit distributed storage and store it into your local filesystem''',
        "subs": lambda: dict(repo_option, **additional_options),
    },
    "init": {
        "help": '''initializes a ml-git repository''',
        "subs": lambda: dict(reponame_option)
    },
    "init-metadata": {
        "help": '''initializes ml-git metadata repositories''',
        "subs": lambda: dict()
    },
    "show": {
        "help": '''shows machine learning model specification details''',
        "subs": lambda: dict(repo_option, **additional_options),
    },
}


def parse_options(cmds_list):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="cmd")
    for cmds in cmds_list:
        for cmd, spec in cmds.items():
            help = spec["help"]
            subparser = subparsers.add_parser(cmd, help=help)
            for option, ospec in spec["subs"]().items():
                help = ospec["help"]
                try:
                    default = ospec["default"]
                    subparser.add_argument(option, default=default, help=help)
                except:
                    subparser.add_argument(option, help=help)
    return parser.parse_args()


def parsed_options(type="model"):
    global additional_options
    if type == "dataset":
        additional_options = dataset_option
    elif type == "labels":
        additional_options = label_option

    return parse_options([command_usage, command_usage1])
