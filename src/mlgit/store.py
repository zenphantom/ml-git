"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import ipfsapi
from mlgit.config import get_key
from mlgit import log
import os
import boto3
from pprint import pprint

def store_factory(config, store_string):
    stores = { "s3" : S3Store, "ipfs" : IPFSStore }
    sp = store_string.split('/')

    try:
        store_type = sp[0][:-1]
        bucket_name = sp[2]
        log.info("Store Factory: store [%s] ; bucket [%s]" % (store_type, bucket_name))

        bucket = config["store"]["s3"][bucket_name]

        return stores[store_type](bucket_name, bucket)
    except Exception as e:
        log.error("Store Factory: exception: [%s]" % (e))
        return None

class StoreFile(object):
    def __init__(self, hash):
        self.__hash = hash
        self.__version = "immutable"

    def __init__(self, file, version):
        self.__file = file
        self.__version = version

    def metadata(self):
        try:
            return self.__hash
        except:
            return "__".join([self.__file, self.__version])

    def file(self):
        try:
            return self.__hash, self.__version
        except:
            return self.__file, self.__version


class Store(object):
    def __init__(self):
        self.connect()

    def connect(self):
        pass

    def put(self, keypath, filepath):
        pass

    def get_by_hash(self, hash):
        pass

    def store(self, key, file, path, prefix=None):
        full_path = os.sep.join([path, file])

        if os.path.isdir(full_path) == True:
            return self.__dir_store(key, path, prefix) #TODO add prefix in story & full path
        else:
            return self.__file_store(key, full_path, prefix)

    #def __dir_store(self, name, dirname, prefix=None): # TODO : recursive => subdirs must be part of key!
    #    hfiles = []
    #    for root, dirs, files in os.walk(dirname):
    #        for file in files:
    #            full_path= os.sep.join([root, file])
    #            log.info("store: adding %s to %s store" % (full_path, self.__store_type))

    #            uri = self.put(key, full_path)
    #            hfiles.append( {file: uri} )
    #    return hfiles

    def __file_store(self, key, filepath, prefix=None):
        keypath = key
        if prefix is not None:
            keypath = prefix + '/' + key

        uri = self.put(keypath, filepath)
        return [ {key: uri} ]

class S3Store(Store):
    def __init__(self, bucket_name, bucket):
        self.__store_type = "S3"
        self.__profile = bucket["aws-credentials"]["profile"]
        self.__region = get_key("region", bucket)
        self.__bucket = bucket_name
        super(S3Store, self).__init__()

    def connect(self):
        log.info("S3Store connect: profile [%s] ; region [%s]" % (self.__profile, self.__region))
        self.__session = boto3.Session(profile_name=self.__profile, region_name=self.__region)
        self.__store = self.__session.resource('s3')

    def create_bucket_name(self, bucket_prefix):
        import uuid
        # The generated bucket name must be between 3 and 63 chars long
        return ''.join([bucket_prefix, str(uuid.uuid4())])

    def create_bucket(self, bucket_prefix):
        s3_connection = self.__store
        current_region = self.__session.region_name
        bucket_name = self.create_bucket_name(bucket_prefix)
        print(bucket_name, current_region)
        bucket_response = s3_connection.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': current_region})
        return bucket_name, bucket_response

    def _to_uri(self, keyfile, version=None):
        if version is not None:
            return keyfile + '?version=' + version
        return keyfile

    def put(self, keypath, filepath):
        bucket = self.__bucket
        s3_resource = self.__store

        res = s3_resource.Bucket(bucket).Object(keypath).put(filepath, Body=open(filepath, 'rb')) # TODO :test for errors here!!!
        pprint(res)
        try:
            version = res['VersionId']
        except:
            log.error("S3Store put: bucket [%s] not configured with Versioning" % (bucket))
            version = None

        log.info("S3Store put: stored [%s] in bucket [%s] with key [%s]-[%s]" % (filepath, bucket, keypath, version))
        return self._to_uri(keypath, version)

    def _to_file(self, uri):
        sp = uri.split('?')
        if len(sp) < 2: return uri, None

        key = sp[0]

        v = "version="
        remain = ''.join(sp[1:])
        vremain = remain[:len(v)]
        if vremain != v: return uri, None

        version = remain[len(v):]
        return key, version

    def get(self, filepath, reference):
        key, version = self._to_file(reference)
        return self.__get(filepath, key, version=version)

    def __get(self, file, keypath, version=None):
        bucket = self.__bucket
        s3_resource = self.__store
        if version is not None:

            res = s3_resource.Object(bucket, keypath).get(f'/tmp/{file}', VersionId=version)
            r = res["Body"]
            log.info("S3 Store get: downloading [%s], version [%s], from bucket [%s] into file [%s]" % (keypath, version, bucket, file))
            with open(file, 'wb') as f:
                while True:
                    chunk = r.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
        else:
            return s3_resource.Object(bucket, keypath).download_file(file)

class IPFSStore(object):
    def __init__(self, store="global"):
        super(IPFSStore, self).__init__()

    def connect(self):
        self.__ipfs = ipfsapi.connect(self.node, self.port)

    def put(self, file):
        k = self.__ipfs.add(file)
        return k

    def get(self, filepath, reference): #TODO :re-implement with link, unlink here
        self.__ipfs.get(reference)
        try:
            os.link(v, os.path.join(full_path, k))
        except FileExistsError:
            pass
        os.unlink(v)


    def _to_uri(self, keyfile, version=None):
        return "ipfs://" + keyfile

    def store(self, key, path):
        if os.path.isdir(path):
            return self.__dir_store(key, path)
        else:
            return self.__file_store(key, path)

    def __dir_store(self, name, dirname):
        hfiles = []
        for root, dirs, files in os.walk(dirname):
            for file in files:
                full_path= os.path.join(root, file)
                log.info("model store: adding %s to IPFS store" % (full_path))
                ipfs_k = self.put(full_path)
                uri = self._to_uti(ipfs_k)
                hfiles.append( {file: uri} )
        return hfiles

    def __file_store(self, name, filename):
        ipfs_k = self.put(filename)
        return [ {name: ipfs_k["Hash"]} ]

#def get_by_name(category, subcategory, model_name):
#    model_hash = metadata_get_hash(category, subcategory, model_name)
#    return get_by_hash(model_hash)

if __name__=="__main__":
    bucket = {
        "aws-credentials" : { "profile" : "personal"},
        "region" : "us-east-1"
    }
    s3 = S3Store("ml-git-models", bucket)
    #print(s3.create_bucket("ml-git-models"))
    #print(s3.put("test.dat"))
    #print(s3.get("models/test-vision/test.dat", version='gEAkOx.ryMifOKZjLRrsnK4mYQVD3WjC'))
    #print(s3.get("vision-computing/images/cifar-10/cifar-10.pkl.tar.gz", "cifar-10.pkl.tar.gz", version='dZlanT4yZmPf2pBX5MNJsVfU1u1ZSVbi'))
    #print(s3.get("models/test-vision/test.dat"))
    #
    #

    print(s3._to_file("vision-computing/images/cifar-10/cifar-10.pkl.tar.gz?version=dZlanT4yZmPf2pBX5MNJsVfU1u1ZSVbi"))
    #from boto3.session import Session
    #s = Session()
    #print(s.get_available_regions('dynamodb'))
