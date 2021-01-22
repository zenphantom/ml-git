"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
from ml_git.config import get_sample_spec_doc

output_messages = {
    'DEBUG_REMOVE_REMOTE': 'Removing remote from local repository [%s]',

    'INFO_INITIALIZED_PROJECT': 'Initialized empty ml-git repository in %s',
    'INFO_ADD_REMOTE': 'Add remote repository [%s] for [%s]',
    'INFO_CHECKOUT_LATEST_TAG': 'Performing checkout on the entity\'s lastest tag (%s)',
    'INFO_CHECKOUT_TAG': 'Performing checkout in tag %s',
    'INFO_METADATA_INIT': 'Metadata init [%s] @ [%s]',
    'INFO_COMMIT_REPO': 'Commit repo[%s] --- file[%s]',
    'INFO_CHANGING_REMOTE': 'Changing remote from [%s] to [%s] for [%s]',
    'INFO_REMOVE_REMOTE': 'Removing remote repository [%s] from [%s].',
    'INFO_ADD_STORE': 'Add store [%s://%s] with creds from profile [%s]',
    'INFO_ADD_STORE_WITHOUT_PROFILE': 'Add store [%s://%s]',
    'INFO_INITIALIZING_RESET': 'Initializing reset [%s] [%s] of commit. ',
    'INFO_STARTING_GC': 'Starting the garbage collector for %s',
    'INFO_REMOVED_FILES': 'A total of %s files have been removed from %s',
    'INFO_RECLAIMED_SPACE': 'Total reclaimed space %s.',
    'INFO_ENTITY_DELETED': 'Entity %s was deleted',
    'INFO_PUT_STORED': 'Put - stored [%s] in bucket [%s] with key [%s]-[%s]',

    'ERROR_WITHOUT_TAG_FOR_THIS_ENTITY': 'No entity with that name was found.',
    'ERROR_MULTIPLES_ENTITIES_WITH_SAME_NAME': 'You have more than one entity with the same name. Use one of the following tags to perform the checkout:\n',
    'ERROR_WRONG_VERSION_NUMBER_TO_CHECKOUT': 'The version specified for that entity does not exist. Last entity tag:\n\t%s',
    'ERROR_UNINITIALIZED_METADATA': 'You don\'t have any metadata initialized',
    'ERROR_REMOTE_UNCONFIGURED': 'Remote URL not found for [%s]. Check your configuration file.',
    'ERROR_ENTITY_NOT_FOUND': 'Entity type [%s] not found in your configuration file.',
    'ERROR_REMOTE_NOT_FOUND': 'Remote URL not found.',
    'ERROR_MISSING_MUTABILITY': 'Missing option "--mutability".  Choose from:\n\tstrict,\n\tflexible,\n\tmutable.',
    'ERROR_SPEC_WITHOUT_MUTABILITY': 'You need to define a mutability type when creating a new entity. '
                                     'Your spec should look something like this:' + get_sample_spec_doc('some-bucket'),
    'ERROR_AWS_KEY_NOT_EXIST': 'The AWS Access Key Id you provided does not exist in our records.',
    'ERROR_BUCKET_DOES_NOT_EXIST': 'This bucket does not exist -- [%s]',
    'ERROR_INVALID_ENTITY_TYPE': 'The entity type informed is invalid.',
    'ERROR_INVALID_STATUS_DIRECTORY': 'The directory informed is invalid.',
    'ERROR_OBJECT_NOT_FOUND': 'Object [%s] not found',

    'WARN_HAS_CONFIGURED_REMOTE': 'YOU ALREADY HAS A CONFIGURED REMOTE. All data stored in this repository will be sent to the new one on the first push.',
}
