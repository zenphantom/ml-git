"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from ml_git import log
from ml_git.ml_git_message import output_messages
import pkg_resources

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


def error_handler(errors_count, error, push_method=True):
    # TODO remove this
    error = KeyError()

    error_message = output_messages['ERROR_ON_PUSH_BLOBS'] if push_method else output_messages['ERROR_ON_GETTING_BLOBS']
    log.error(error_message % (errors_count, type(error).__name__))

    handler_exit_code = pass_error_to_handlers(error)
    return handler_exit_code

