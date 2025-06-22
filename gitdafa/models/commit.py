#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Commit:
    """
    Model, to reflect commit properties.

    Parameters
    ----------
    commit_id : str
    author : Author, optional
    date : datetime.datetime, optional
    message : str, optional

    Attributes
    ----------
    self._id : str
        commit ID
    self.author : Author
    self.date : datetime.datetime
    self.message : str
    self.changes : list of Change
    """
    def __init__(self,
                 commit_id: str,
                 author=None,
                 date=None,
                 message: str = None):
        self._id = commit_id
        self.author = author
        self.date = date
        self.datetime = None
        self.message = message
        self.changes = []

    def __str__(self):
        return f"Author: {self.author}, " +\
            f"Date: {self.date}, " +\
            f"Message: {self.message}"

    def __repr__(self):
        return f"'author': {self.author.email if self.author else 'None'}, " + \
            f"'date': {self.date}"

    def serialize(self):
        """Returns json serializable dictionary"""
        return {
            "_id": self._id,
            "author": self.author,
            "date": self.date,
            "message": self.message,
            "changes": self.changes,
        }
