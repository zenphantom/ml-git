"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import os

import humanize

from ml_git import log
from ml_git.file_system.hashfs import HashFS
from ml_git.ml_git_message import output_messages
from ml_git.utils import yaml_load, remove_unnecessary_files


class Cache(HashFS):
    def __init__(self, cachepath, datapath='', manifest=''):
        super(Cache, self).__init__(cachepath)
        self.__datapath = datapath
        self.__manifest = manifest

    def update(self):
        objfiles = yaml_load(self.__manifest)
        for key in objfiles:
            files = objfiles[key]

            for file in files:
                srcfile = os.path.join(self.__datapath, file)
                try:
                    self.link(key, srcfile)
                except FileNotFoundError:
                    pass

    def garbage_collector(self, blobs_hashes):
        count_removed_cache, reclaimed_cache_space = remove_unnecessary_files(blobs_hashes, self._path)
        log.debug(output_messages['INFO_REMOVED_FILES'] % (humanize.intword(count_removed_cache), self._path))
        return count_removed_cache, reclaimed_cache_space
