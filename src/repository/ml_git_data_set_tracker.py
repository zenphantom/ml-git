"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os

from utils.constants import *


def is_data_set_tracking_initialized(path):
    return os.path.isfile(os.path.join(path, DATA_SET_TRACKING_FILE))


def initialize_data_set_tracking(data_set_path):
    os.mkdir(data_set_path)
    full_path = os.path.join(data_set_path, DATA_SET_TRACKING_FILE)
    with open(full_path, 'w') as out:
        out.write('## Do not change this file manually. Data set files will automatically be added here.\n')
