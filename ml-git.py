"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

#!/usr/bin/env python3

from mlgit.config import config_load
# from mlgit.log import init_logger
from mlgit import log
from mlgit.options import parsed_options

if __name__ == "__main__":
    config_load()
    log.init_logger()

    log.error("bouh")

    args = parsed_options("model")

    if args.type == "model":
        pass
    elif args.type == "labels":
        pass
    else:
        log.error("see help")
    #
    # if args.cmd == 'add':
    #     model_spec = args.model
    #     force = args.force
    #     repo = args.repository
    #     # m = ModelManager(repo, force)
    #     m.model_store(model_spec)
    # if args.cmd == 'get':
    #     model_spec = args.model
    #     repo = args.repository
    #     # m = ModelManager(repo)
    #     print(model_spec)
    #     m.model_get(model_spec)
    # # elif arg1 == "search":
    # if args.cmd == 'list':
    #     repo = args.repository
    #     # m = ModelManager(repo)
    #     m.list()
    # if args.cmd == "show":
    #     model_name = args.model
    #     repo = args.repository
    #     m = ModelManager(repo)
    #     m.show(model_name)
    # if args.cmd == "publish":
    #     repo = args.repository
    #     m = ModelManager(repo)
    #     m.publish()
    # if args.cmd == "update":
    #     repo = args.repository
    #     m = ModelManager(repo)
    #     m.update()
