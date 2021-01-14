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


class SFtpStore(Store):
    def __init__(self, bucket_name, bucket):
        self._store_type = StoreType.SFTPH
        self._username = bucket['username']
        self._key = bucket['ssh-key']
        self._host = get_key('endpoint-url', bucket)

        self._bucket = bucket_name
        super(SFtpStore, self).__init__()

    def connect(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        user_key = paramiko.RSAKey.from_private_key_file(self._key)
        ssh_client.connect(self._host, port=22, username=self._username, pkey=user_key)

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

    def create_bucket_name(self, bucket_prefix):
        import uuid
        # The generated bucket name must be between 3 and 63 chars long
        return ''.join([bucket_prefix, str(uuid.uuid4())])

    def create_bucket(self, bucket_prefix):
        bucket_name = self.create_bucket_name(bucket_prefix)

        try:
            self._store.chdir(bucket_name)
        except IOError:
            self._store.mkdir(bucket_name)

    def _to_uri(self, keyfile, version=None):
        if version is not None:
            return keyfile + '?version=' + version
        return keyfile

    def put(self, key_path, file_path):
        bucket = self._bucket

        with open(file_path, 'rb') as text_file:
            self._store.put(file_path, os.path.join(self._bucket, os.path.basename(text_file.name)))

        version = None

        log.info(output_messages['INFO_PUT_STORED'] % (file_path, bucket, key_path, version),
                 class_name=SFTPSTORE_NAME)
        return self._to_uri(key_path, version)

    def put_object(self, file_path, obj):
        self._store.putfo(obj, file_path)

    @staticmethod
    def _to_file(uri):
        sp = uri.split('?')
        if len(sp) < 2:
            return uri, None

        key = sp[0]
        v = 'version='
        remain = ''.join(sp[1:])
        vremain = remain[:len(v)]
        if vremain != v:
            return uri, None

        version = remain[len(v):]
        return key, version

    def get(self, file_path, reference):
        key, version = self._to_file(reference)
        return self._get(file_path, key, version=version)

    def get_object(self, key_path):
        try:
            self._store.chdir(os.path.join(self._bucket, key_path))
            raise RuntimeError('Object [%s] not found' % key_path)
        except IOError:
            res = self._store.open(os.path.join(self._bucket, key_path))
            return res.read(res.stat().st_size)

    def _get(self, file, key_path, version=None):
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
