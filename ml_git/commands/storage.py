"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

from click_didyoumean import DYMGroup

from ml_git.commands.repository import repository


@repository.group('storage', help='Storage management for this ml-git repository.', cls=DYMGroup)
def storage():
    """
    Storage management for this ml-git repository.
    """
    pass
