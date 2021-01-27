"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import os
import shutil
import tempfile

from ml_git import log, admin
from ml_git.admin import init_mlgit
from ml_git.config import config_load
from ml_git.constants import StoreType, EntityType
from ml_git.repository import Repository
from ml_git.log import init_logger

init_logger()


def get_repository_instance(repo_type):
    return Repository(config_load(), repo_type)


def validate_sample(sampling):
    if 'group' in sampling or 'random' in sampling:
        if 'seed' not in sampling:
            log.error('It is necessary to pass the attribute \'seed\' in \'sampling\'. Example: {\'group\': \'1:2\', '
                      '\'seed\': \'10\'}.')
            return False
    elif 'range' not in sampling:
        log.error('To use the sampling option, you must pass a valid type of sampling (group, '
                  'random or range).')
        return False
    return True


def checkout(entity, tag, sampling=None, retries=2, force=False, dataset=False, labels=False, version=-1):
    """This command allows retrieving the data of a specific version of an ML entity.

    Example:
        checkout('dataset', 'computer-vision__images3__imagenet__1')

    Args:
        entity (str): The type of an ML entity. (dataset, labels or model)
        tag (str): An ml-git tag to identify a specific version of an ML entity.
        sampling (dict): group: <amount>:<group> The group sample option consists of amount and group used to
                                 download a sample.\n
                         range: <start:stop:step> The range sample option consists of start, stop and step used
                                to download a sample. The start parameter can be equal or greater than zero. The
                                stop parameter can be 'all', -1 or any integer above zero.\n
                         random: <amount:frequency> The random sample option consists of amount and frequency
                                used to download a sample.
                         seed: The seed is used to initialize the pseudorandom numbers.
        retries (int, optional): Number of retries to download the files from the storage [default: 2].
        force (bool, optional): Force checkout command to delete untracked/uncommitted files from the local repository [default: False].
        dataset (bool, optional): If exist a dataset related with the model or labels, this one must be downloaded [default: False].
        labels (bool, optional): If exist labels related with the model, they must be downloaded [default: False].

    Returns:
        str: Return the path where the data was checked out.

    """

    repo = Repository(config_load(), entity)
    repo.update()
    if sampling is not None and not validate_sample(sampling):
        return None
    options = {}
    options['with_dataset'] = dataset
    options['with_labels'] = labels
    options['retry'] = retries
    options['force'] = force
    options['bare'] = False
    options['version'] = version
    repo.checkout(tag, sampling, options)

    data_path = os.path.join(entity, *tag.split('__')[:-1])
    if not os.path.exists(data_path):
        data_path = None
    return data_path


def clone(repository_url, folder=None, track=False):
    """This command will clone minimal configuration files from repository-url with valid .ml-git/config.yaml,
    then initialize the metadata according to configurations.

    Example:
        clone('https://git@github.com/mlgit-repository')

    Args:
        repository_url (str): The git repository that will be cloned.
        folder (str, optional): Directory that can be created to execute the clone command [default: current path].
        track (bool, optional): Set if the tracking of the cloned repository should be kept [default: False].

    """

    repo = Repository(config_load(), 'project')
    if folder is not None:
        repo.clone_config(repository_url, folder, track)
    else:
        current_directory = os.getcwd()
        with tempfile.TemporaryDirectory(dir=current_directory) as tempdir:
            mlgit_path = os.path.join(tempdir, 'mlgit')
            repo.clone_config(repository_url, mlgit_path, track)
            if not os.path.exists(os.path.join(current_directory, '.ml-git')):
                shutil.move(os.path.join(mlgit_path, '.ml-git'), current_directory)
            os.chdir(current_directory)


def add(entity_type, entity_name, bumpversion=False, fsck=False, file_path=[], metrics_file='', metric=''):
    """This command will add all the files under the directory into the ml-git index/staging area.

    Example:
        add('dataset', 'dataset-ex', bumpversion=True)

    Args:
        entity_type (str): The type of an ML entity. (dataset, labels or model)
        entity_name (str): The name of the ML entity you want to add the files.
        bumpversion (bool, optional): Increment the entity version number when adding more files [default: False].
        fsck (bool, optional): Run fsck after command execution [default: False].
        file_path (list, optional): List of files that must be added by the command [default: all files].
        metrics_file (str, optional): The metrics file path [default: empty].
        metric (str, float, optional): The metric keys and values [default: empty].
    """

    repo = Repository(config_load(), entity_type)
    repo.add(entity_name, file_path, bumpversion, fsck, metric, metrics_file)


def commit(entity, ml_entity_name, commit_message=None, related_dataset=None, related_labels=None):
    """That command commits the index / staging area to the local repository.

    Example:
        commit('dataset', 'dataset-ex')

    Args:
        entity (str): The type of an ML entity. (dataset, labels or model).
        ml_entity_name (str): Artefact name to commit.
        commit_message (str, optional): Message of commit.
        related_dataset (str, optional): Artefact name of dataset related to commit.
        related_labels (str, optional): Artefact name of labels related to commit.
    """

    repo = get_repository_instance(entity)

    specs = dict()

    if related_dataset:
        specs['dataset'] = related_dataset

    if related_labels:
        specs['labels'] = related_labels

    repo.commit(ml_entity_name, specs, msg=commit_message)


def push(entity, entity_name,  retries=2, clear_on_fail=False):
    """This command allows pushing the data of a specific version of an ML entity.

        Example:
            push('dataset', 'dataset-ex')

        Args:
            entity (str): The type of an ML entity. (dataset, labels or model).
            entity_name (str): An ml-git entity name to identify a ML entity.
            retries (int, optional): Number of retries to upload the files to the storage [default: 2].
            clear_on_fail (bool, optional): Remove the files from the store in case of failure during the push operation [default: False].
    """

    repo = Repository(config_load(), entity)
    repo.push(entity_name, retries, clear_on_fail)


def create(entity, entity_name, categories, mutability, **kwargs):
    """This command will create the workspace structure with data and spec file for an entity and set the store configurations.

        Example:
            create('dataset', 'dataset-ex', categories=['computer-vision', 'images'], mutability='strict')

        Args:
            entity (str): The type of an ML entity. (dataset, labels or model).
            entity_name (str): An ml-git entity name to identify a ML entity.
            categories (list): Artifact's category name.
            mutability (str): Mutability type. The mutability options are strict, flexible and mutable.
            store_type (str, optional): Data store type [default: s3h].
            version (int, optional): Number of retries to upload the files to the storage [default: 2].
            import_path (str, optional): Path to be imported to the project.
            bucket_name (str, optional): Bucket name.
            import_url (str, optional): Import data from a google drive url.
            credentials_path (str, optional): Directory of credentials.json.
            unzip (bool, optional): Unzip imported zipped files [default: False].
    """

    args = {'artifact_name': entity_name, 'category': categories, 'mutability': mutability,
            'version_number': kwargs.get('version', 1), 'import': kwargs.get('import_path', None),
            'store_type':  kwargs.get('store_type', StoreType.S3H.value),
            'bucket_name': kwargs.get('bucket_name', None), 'unzip': kwargs.get('unzip', False),
            'import_url': kwargs.get('import_url', None), 'credentials_path': kwargs.get('credentials_path', None),
            'wizard_config': False}

    repo = Repository(config_load(), entity)
    repo.create(args)


def init(entity):
    """This command will start the ml-git entity.

        Examples:
            init('repository')
            init('dataset')

        Args:
            entity (str): The type of entity that will be initialized (repository, dataset, labels or model).
    """

    if entity == 'repository':
        init_mlgit()
    elif entity in EntityType.to_list():
        repo = Repository(config_load(), entity)
        repo.init()
    else:
        log.error('The type of entity entered is invalid. Valid types are: [repository, dataset, labels or model]')


def store_add(bucket_name, bucket_type=StoreType.S3H.value, credentials=None, global_configuration=False,
              endpoint_url=None, username=None, private_key=None, port=22):
    """This command will add a store to the ml-git project.

        Examples:
            store_add('my-bucket', type='s3h')

        Args:
            bucket_name (str): The name of the bucket in the storage.
            bucket_type (str, optional): Store type (s3h, azureblobh or gdriveh) [default: s3h].
            credentials (str, optional): Name of the profile that stores the credentials or the path to the credentials.
            global_configuration (bool, optional): Use this option to set configuration at global level [default: False].
            endpoint_url (str, optional): Store endpoint url.
            username (str, optional): The username for the sftp login.
            private_key (str, optional): Full path for the private key file.
    """

    if bucket_type not in StoreType.to_list():
        log.error('Aqui2')
        return

    sftp_configs = {'username': username,
                    'private_key': private_key,
                    'port': port}
    admin.store_add(bucket_type, bucket_name, credentials, global_configuration, endpoint_url, sftp_configs=sftp_configs)


def remote_add(entity, remote_url, global_configuration=False):
    """This command will add a remote to store the metadata from this ml-git project.

        Examples:
            remote_add('dataset', 'https://git@github.com/mlgit-datasets')

        Args:
            entity (str): The type of an ML entity. (repository, dataset, labels or model).
            remote_url(str): URL of an existing remote git repository.
            global_configuration (bool, optional): Use this option to set configuration at global level [default: False].
    """

    repo = Repository(config_load(), entity)
    repo.repo_remote_add(entity, remote_url, global_configuration)
