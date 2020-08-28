#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Author:
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

    def add_commit(self, commit: list):
        for change in commit.changes:
            self.lines_added += change.added
            self.lines_deleted += change.deleted
        self.commits.append(commit)

    def __eq__(self):
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
