"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
from ml_git import log
from ml_git.config import get_key
from ml_git.constants import SFTPSTORE_NAME, StoreType
from ml_git.ml_git_message import output_messages
from ml_git.storages.store import Store

import paramiko

from ml_git.utils import posix_path


class SFtpStore(Store):
    def __init__(self, bucket_name, bucket):
        self._store_type = StoreType.SFTPH
        self._username = bucket['username']
        self._private_key = bucket['private-key']
        self._host = get_key('endpoint-url', bucket)

        self._bucket = bucket_name
        super(SFtpStore, self).__init__()

    def connect(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        user_private_key = paramiko.RSAKey.from_private_key_file(self._private_key)
        ssh_client.connect(self._host, port=22, username=self._username, pkey=user_private_key)

        open_session = ssh_client.get_transport().open_session()
        paramiko.agent.AgentRequestHandler(open_session)

        self._store = ssh_client.open_sftp()
        self._store.chdir("./")

    def bucket_exists(self):
        try:
            self._store.chdir(self._bucket)
        except IOError:
            error_msg = output_messages['ERROR_BUCKET_DOES_NOT_EXIST'] % self._bucket
            log.error(error_msg, class_name=SFTPSTORE_NAME)
            return False
        return True

    def put(self, key_path, file_path):
        self._store.put(file_path, posix_path(os.path.join(self._bucket, key_path)))
        version = None
        log.debug(output_messages['INFO_PUT_STORED'] % (file_path, self._bucket, key_path, version), class_name=SFTPSTORE_NAME)
        return key_path

    def put_object(self, file_path, obj):
        self._store.putfo(obj, file_path)

    def get(self, file_path, reference):
        try:
            self._store.get(posix_path(os.path.join(self._bucket, reference)), file_path)
            return True
        except Exception:
            log.error('Object [%s] not found' % reference, class_name=SFTPSTORE_NAME)
            return False

    def get_object(self, key_path):
        try:
            self._store.chdir(os.path.join(self._bucket, key_path))
            raise RuntimeError('Object [%s] not found' % key_path)
        except IOError:
            res = self._store.open(os.path.join(self._bucket, key_path))
            return res.read(res.stat().st_size)

    def delete(self, file_path, reference):
        self._store.remove(os.path.join(self._bucket, file_path))
        return True

    def list_files_from_path(self, path):
        files = self._store.listdir(os.path.join(self._bucket, path))
        return list(filter(lambda item: item[-1] != '/', files))
