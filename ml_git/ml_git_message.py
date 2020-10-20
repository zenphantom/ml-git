"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

output_messages = {
    'INFO_INITIALIZED_PROJECT': 'Initialized empty ml-git repository in %s',
    'INFO_ADD_REMOTE': 'Add remote repository [%s] for [%s]',
    'INFO_CHECKOUT_LATEST_TAG': 'Performing checkout on the entity\'s lastest tag (%s)',
    'INFO_CHECKOUT_TAG': 'Performing checkout in tag %s',
    'INFO_METADATA_INIT': 'Metadata init [%s] @ [%s]',
    'INFO_COMMIT_REPO': 'Commit repo[%s] --- file[%s]',
    'INFO_CHANGING_REMOTE': 'Changing remote from [%s] to [%s] for [%s]',

    'ERROR_WITHOUT_TAG_FOR_THIS_ENTITY': 'No entity with that name was found.',
    'ERROR_MULTIPLES_ENTITIES_WITH_SAME_NAME': 'You have more than one entity with the same name. Use one of the following tags to perform the checkout:\n',
    'ERROR_WRONG_VERSION_NUMBER_TO_CHECKOUT': 'The version specified for that entity does not exist. Last entity tag:\n\t%s',
    'ERROR_UNINITIALIZED_METADATA': 'You don\'t have any metadata initialized',

    'WARN_HAS_CONFIGURED_REMOTE': 'YOU ALREADY HAS A CONFIGURED REMOTE. All data stored in this repository will be sent to the new one on the first push.',
}
