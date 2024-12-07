#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .model_interafce import TableInterface


class Author(TableInterface):
    """
    Model, to reflect commit author properties and function.

    Parameters
    ----------
    name : str, optional
    email : str, optional

    Attributes
    ----------
    self.name : str
    self.email : str
    self.commits : list of Commits
    self.lines_added : int
    self.lines_delete : int

    Properties
    ----------
    commits_count : int

    Methods
    -------
    add_commit(commit)
    get_table_row()
    get_table_headers()
    serialize()
    """
    def __init__(self, name: str = None, email: str = None):
        self.name: str = name
        self.email: str = email
        self.commits: list = []
        self.lines_added: int = 0
        self.lines_deleted: int = 0

    @property
    def commits_count(self):
        return self.commits_count

    @commits_count.getter
    def commits_count(self):
        return len(self.commits)

    def add_commit(self, commit):
        """
        Add commit to the attribute commits list and
        increment lines_added and lines_deleted attributes

        Parameters
        ----------
        commit : Commit
            Object of the Commit model class

        Returns
        -------
        None
        """
        for change in commit.changes:
            self.lines_added += change.added
            self.lines_deleted += change.deleted
        self.commits.append(commit)

    def get_table_row(self) -> []:
        return [self.name,
                self.email,
                self.commits_count,
                self.lines_added,
                self.lines_deleted]

    def get_table_headers(self) -> []:
        return ["Name",
                "Email",
                "Commits",
                "Lines added",
                "Lines deleted"]

    def serialize(self):
        """Returns json serializable dictionary"""
        return {
            'name': self.name,
            'email': self.email,
            'commits': self.commits,
            'lines_added': self.lines_added,
            'lines_deleted': self.lines_deleted,
        }

    def __eq__(self, item):
        if item.email == self.email:
            return True
        else:
            return False

    def __str__(self):
        return f"Name: {self.name}, " + \
               f"Email: {self.email}, " + \
               f"Commits: {self.commits_count}"

    def __repr__(self):
        return f"'name': '{self.name}',  " + \
               f"'email': '{self.email}', " + \
               f"'Commits': {self.commits_count}"
