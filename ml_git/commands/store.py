"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from click_didyoumean import DYMGroup

from ml_git.commands.repository import repository


@repository.group('store', help='[DEPRECATED]: Store management for this ml-git repository.', cls=DYMGroup)
def store():
    """
    Store management for this ml-git repository.
    """
    pass
