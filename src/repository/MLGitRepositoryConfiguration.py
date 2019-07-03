"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

class MLGitRepositoryConfiguration:
    def __init__(self, name, version, labels, data_store):
        self.name = name
        self.version = version
        self.labels = labels
        self.data_store = data_store
