"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
from enum import unique, Enum

import pkg_resources
from botocore.exceptions import ClientError
from ml_git import log
from ml_git.ml_git_message import output_messages

entry_point = 'mlgit.error_handler'
error_handler_method_name = 'error_handler'


def pass_error_to_handlers(error):
    handler = {}
    for ep in pkg_resources.iter_entry_points(group=entry_point):
        handler.update({ep.name: ep.load()})
    exit_code = 1
    if len(handler) > 0 and error_handler_method_name in handler:
        exit_code = handler[error_handler_method_name](error)
    return exit_code


def error_handler(error):
    log.error(output_messages['ERROR_FOUND'] % (type(error).__name__, error))
    handler_exit_code = pass_error_to_handlers(error)
    return handler_exit_code


@unique
class CriticalErrors(Enum):
    CLIENT_ERROR = ClientError

    @staticmethod
    def to_list():
        return [error.value for error in CriticalErrors]
