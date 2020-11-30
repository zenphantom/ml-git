"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import io
import os

from pkg_resources import resource_string


def _get_version_info(file_name):
    file_stream = io.StringIO(resource_string(__name__, file_name).decode('utf-8'))
    return _read_info_file(file_stream)


def _get_build_number(file_name):
    build_number_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'build'))
    build_version_info_path = os.path.join(build_number_file_path, file_name)
    if os.path.exists(build_version_info_path):
        file_stream = open(os.path.abspath(build_version_info_path), encoding='utf-8')
        return _read_info_file(file_stream)
    return None


def _read_info_file(file_stream):

    line = file_stream.readline().strip()
    dict_info = {}
    while line:
        line_info = line.split('=')
        dict_info[line_info[0]] = line_info[1]
        line = file_stream.readline().strip()
    file_stream.close()
    return dict_info


def get_version():
    version_file_name = 'version.info'
    version_info = _get_version_info(version_file_name)
    __version__ = '{}.{}.{}'.format(version_info['MAJOR_VERSION'], version_info['MINOR_VERSION'], version_info['PATCH_VERSION'])

    build_number = _get_build_number(version_file_name)

    if build_number:
        __version__ += '-' + build_number['BUILD_NUMBER']

    return __version__
