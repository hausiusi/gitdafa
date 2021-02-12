#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .model_interafce import TableInterface


class Tag(TableInterface):

    def __init__(self, sha: str, name: str, commits: list, index: int = 0):
        """
        @summary Tag object holding tag related data
        @param sha: tag hash
        @param name: tag name
        @param index: tag index (starts from 0)
        @param commits: commits under the specified tag
        """
        self.sha: str = sha
        self.name: str = name
        self.index: int = index
        self.commits: list = commits

    @property
    def commits_count(self):
        return self.commits_count

    @commits_count.getter
    def commits_count(self):
        return len(self.commits)

    def get_table_row(self) -> []:
        return [self.name, self.sha, self.index, self.commits_count]

    def get_table_headers(self) -> []:
        return ["Name", "SHA", "Index", "Commits"]
