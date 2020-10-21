"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

output_messages = {
    'INFO_CHECKOUT_LATEST_TAG': 'Performing checkout on the entity\'s lastest tag (%s)',
    'INFO_CHECKOUT_TAG': 'Performing checkout in tag %s',
    'INFO_METADATA_INIT': 'Metadata init [%s] @ [%s]',
    'INFO_COMMIT_REPO': 'Commit repo[%s] --- file[%s]',
    'INFO_REMOVE_REMOTE': 'Removing remote repository [%s] from [%s].',

    'ERROR_WITHOUT_TAG_FOR_THIS_ENTITY': 'No entity with that name was found.',
    'ERROR_MULTIPLES_ENTITIES_WITH_SAME_NAME': 'You have more than one entity with the same name. Use one of the following tags to perform the checkout:\n',
    'ERROR_WRONG_VERSION_NUMBER_TO_CHECKOUT': 'The version specified for that entity does not exist. Last entity tag:\n\t%s',
    'ERROR_UNINITIALIZED_METADATA': 'You don\'t have any metadata initialized',
    'ERROR_REMOTE_UNCONFIGURED': 'Remote URL not found for [%s]. Check your configuration file.',
    'ERROR_ENTITY_NOT_FOUND': 'Entity type [%s] not found in your configuration file.',
    'ERROR_REMOTE_NOT_FOUND': 'Remote URL not found.',

    'DEBUG_REMOVE_REMOTE': 'Removing remote from local repository [%s]'
}
