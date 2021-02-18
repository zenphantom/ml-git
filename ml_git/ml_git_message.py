"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

doc = '''
  datasets:
    categories:
    - vision-computing
    - images
    mutability: strict
    manifest:
      files: MANIFEST.yaml
      storage: s3h://some-bucket
    name: datasets-ex
    version: 5
'''

output_messages = {
    'DEBUG_REMOVE_REMOTE': 'Removing remote from local repository [%s]',
    'DEBUG_BUILDING_STORAGE_LOG': 'Building the storage.log with these added files',
    'DEBUG_OBJECT_ALREADY_IN_STORAGE': 'Object [%s] already in %s storage',
    'DEBUG_STORAGE_AND_BUCKET': 'Storage [%s] ; bucket [%s]',
    'DEBUG_CHECKSUM_VERIFIED': 'Checksum verified for chunk [%s]',
    'DEBUG_KEY_PATH_ALREADY_EXISTS': 'Key path [%s] already exists in drive path [%s].',
    'DEBUG_CONNECT_PROFILE_AND_REGION': 'Connect - profile [%s] ; region [%s]',
    'DEBUG_CONNECTING_TO_STORAGE': 'Connecting to [%s]',
    'DEBUG_DOWNLOADING_FROM_BUCKET': 'Get - downloading [%s]  from bucket [%s] into file [%s]',
    'DEBUG_DELETING_FROM_BUCKET': 'Delete - deleting [%s] from bucket [%s]',
    'DEBUG_FILE_NOT_IN_LOCAL_REPOSITORY': 'File [%s] not present in local repository',
    'DEBUG_CONTAINER_ALREADY_EXISTS': 'Container %s already exists',
    'DEBUG_AZURE_CLI_NOT_FIND': 'Azure cli configurations not find.',
    'DEBUG_PUSH_BLOB_TO_STORAGE': 'LocalRepository: push blob [%s] to storage',
    'DEBUG_DELETE_BLOB_FROM_STORAGE': 'Delete blob [%s] from storage',
    'DEBUG_CHECK_IPLD': 'LocalRepository: check ipld [%s] in storage',

    'INFO_INITIALIZED_PROJECT': 'Initialized empty ml-git repository in %s',
    'INFO_ADD_REMOTE': 'Add remote repository [%s] for [%s]',
    'INFO_CHECKOUT_LATEST_TAG': 'Performing checkout on the entity\'s lastest tag (%s)',
    'INFO_CHECKOUT_TAG': 'Performing checkout in tag %s',
    'INFO_METADATA_INIT': 'Metadata init [%s] @ [%s]',
    'INFO_COMMIT_REPO': 'Commit repo[%s] --- file[%s]',
    'INFO_CHANGING_REMOTE': 'Changing remote from [%s] to [%s] for [%s]',
    'INFO_REMOVE_REMOTE': 'Removing remote repository [%s] from [%s].',
    'INFO_ADD_STORAGE': 'Add storage [%s://%s] with creds from profile [%s]',
    'INFO_ADD_STORAGE_WITHOUT_PROFILE': 'Add storage [%s://%s]',
    'INFO_INITIALIZING_RESET': 'Initializing reset [%s] [%s] of commit. ',
    'INFO_STARTING_GC': 'Starting the garbage collector for %s',
    'INFO_REMOVED_FILES': 'A total of %s files have been removed from %s',
    'INFO_RECLAIMED_SPACE': 'Total reclaimed space %s.',
    'INFO_ENTITY_DELETED': 'Entity %s was deleted',
    'INFO_PUT_STORED': 'Put - stored [%s] in bucket [%s] with key [%s]-[%s]',
    'INFO_WRONG_ENTITY_TYPE': 'Metrics cannot be added to this entity: [%s].',
    'INFO_DIRECTORY_STRUCTURE_WRONG': 'It was observed that the directories of this project follow the scheme of old versions of ml-git.\n'
                                      '\tTo continue using this project it is necessary to update the directories. Ml-git can do this update on its own.',
    'INFO_WANT_UPDATE_NOW': '\tDo you want to update your project now? (Yes/No) ',
    'INFO_PROJECT_UPDATE_SUCCESSFULLY': 'Project updated successfully',
    'INFO_ASSOCIATE_DATASETS': 'Associate datasets [%s]-[%s] to the %s.',
    'INFO_UPDATE_THE_PROJECT': 'It was observed that the directories of this project follow the scheme of old versions of ml-git.\n' +
                               '\tTo continue using this project it is necessary to update the directories.',
    'INFO_REMOVED_STORAGE': 'Removed storage [%s://%s] from configuration file.',

    'INFO_AKS_IF_WANT_UPDATE_PROJECT': '\tDo you want to update your project now? (Yes/No) ',
    'INFO_FILE_STORED_IN_BUCKET': 'Put - stored [%s] in bucket [%s] with key [%s]-[%s]',
    'INFO_PARANOID_MODE_ACTIVE': 'Paranoid mode is active - Downloading files: ',
    'INFO_FIXING_CORRUPTED_FILES_IN_STORAGE': 'Fixing corrupted files in remote storage',
    'INFO_EXPORTING_TAG': 'Exporting tag [%s] from [%s] to [%s].',


    'ERROR_WITHOUT_TAG_FOR_THIS_ENTITY': 'No entity with that name was found.',
    'ERROR_MULTIPLES_ENTITIES_WITH_SAME_NAME': 'You have more than one entity with the same name. Use one of the following tags to perform the checkout:\n',
    'ERROR_WRONG_VERSION_NUMBER_TO_CHECKOUT': 'The version specified for that entity does not exist. Last entity tag:\n\t%s',
    'ERROR_UNINITIALIZED_METADATA': 'You don\'t have any metadata initialized',
    'ERROR_REMOTE_UNCONFIGURED': 'Remote URL not found for [%s]. Check your configuration file.',
    'ERROR_ENTITY_NOT_FOUND': 'Entity type [%s] not found in your configuration file.',
    'ERROR_REMOTE_NOT_FOUND': 'Remote URL not found.',
    'ERROR_MISSING_MUTABILITY': 'Missing option "--mutability".  Choose from:\n\tstrict,\n\tflexible,\n\tmutable.',
    'ERROR_SPEC_WITHOUT_MUTABILITY': 'You need to define a mutability type when creating a new entity. '
                                     'Your spec should look something like this:' + doc,
    'ERROR_AWS_KEY_NOT_EXIST': 'The AWS Access Key Id you provided does not exist in our records.',
    'ERROR_BUCKET_DOES_NOT_EXIST': 'This bucket does not exist -- [%s]',
    'ERROR_INVALID_ENTITY_TYPE': 'Invalid entity type. Valid values are:',
    'ERROR_INVALID_STATUS_DIRECTORY': 'The directory informed is invalid.',
    'ERROR_OBJECT_NOT_FOUND': 'Object [%s] not found',
    'ERROR_NO_SUCH_OPTION': 'no such option: %s',
    'ERROR_INVALID_VALUE_FOR': 'Error: Invalid value for "%s": %s',
    'ERROR_NEED_UPDATE_PROJECT': 'To continue using this project it is necessary to update it.',
    'ERROR_PROJECT_NEED_BE_UPDATED': 'To continue using this project it is necessary to update it.',
    'ERROR_UNKNOWN_STORAGE_TYPE': 'Unknown data storage type [%s], choose one of these %s.',
    'ERROR_CORRPUTION_DETECTED': 'Corruption detected for chunk [%s] - got [%s]',
    'ERROR_DRIVE_PATH_NOT_FOUND': 'Drive path [%s] not found.',
    'ERROR_NOT_FOUND': '[%s] not found.',
    'ERROR_FILE_COULD_NOT_BE_UPLOADED': 'The file could not be uploaded: [%s]',
    'ERROR_AUTHETICATION_FAILED': 'Authentication failed',
    'ERROR_BUCKET_NOT_CONFIGURED': 'Put - bucket [%s] not configured with Versioning',
    'ERROR_AZURE_CREDENTIALS_NOT_FOUND': 'Azure credentials could not be found. See the ml-git documentation for how to configure.',
    'ERROR_WITHOUT_STORAGE': 'No storage for [%s]',
    'ERROR_CONFIG_PROFILE_NOT_FOUND': 'The config profile (%s) could not be found',

    'WARN_HAS_CONFIGURED_REMOTE': 'YOU ALREADY HAS A CONFIGURED REMOTE. All data stored in this repository will be sent to the new one on the first push.',
    'WARN_STORAGE_NOT_IN_CONFIG': 'Storage [%s://%s] not found in configuration file.',
    'WARN_EXCPETION_CREATING_STORAGE': 'Exception creating storage -- Configuration not found for bucket [%s]. '
                                       'The available buckets in config file for storage type [%s] are: %s',
    'WARN_REMOVING_FILES_DUE_TO_FAIL': 'Removing %s files from storage due to a fail during the push execution.'
}
