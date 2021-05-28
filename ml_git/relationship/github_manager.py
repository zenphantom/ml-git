"""
© Copyright 2021 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""
import github


class GithubManager:
    """
    Class to manager github operations
    """

    def __init__(self, github_token, url):
        self.__client = github.Github(github_token, base_url=url)

    def get_repos(self):
        """
        Get user repositories
        :return: :class:`github.PaginatedList.PaginatedList` of :class:`github.Repository.Repository
        """
        return self.__client.get_user().get_repos()

    def find_repository(self, repository_name):
        """
        Find repository by name
        :param: repository_name (str). The name of repository.
        :return: :class:`github.Repository.Repository
        """
        return next(iter(self.__client.search_repositories(repository_name)), None)

    @staticmethod
    def file_exists(repository, file_path):
        try:
            repository.get_contents(file_path).type == 'file'
        except github.GithubException:
            return False
        return True

    @staticmethod
    def get_file_content(repository, file_path, ref=github.GithubObject.NotSet):
        try:
            return repository.get_contents(file_path, ref=ref).decoded_content
        except github.GithubException:
            return ''

    @staticmethod
    def search_files_by_extension_in_tag(tag, extension):
        return [file.filename for file in tag.commit.files if extension in file.filename]

    def search_file(self, repository, extension):
        files = self.__client.search_code(query='repo:{} extension:{}'.format(repository.full_name, extension))
        for file in files:
            yield file.path

