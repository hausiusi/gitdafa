import pytest
import sys

sys.path.append("./")

import data_strings as ts
from git import Parse


def test_commit_id():
    assert ts.commit["ID"] == Parse.commit_id(ts.commit["str"])


def test_author():
    assert ts.commit["Author"] == Parse.author(ts.commit["str"])


def test_date():
    assert ts.commit["Date"] == Parse.date(ts.commit['str'])


def test_message():
    assert ts.commit["message"].strip() in Parse.message(ts.commit['str'])


def test_changes():
    assert ts.commit['changes'] == Parse.changes(ts.commit['str'])


def test_committs_by_authors():
    authors = Parse.commits_by_authors(ts.authors["data"])
    for i, author in enumerate(authors):
        assert author['name'] == ts.authors['test_data'][1]['name']
        assert author['name'] == ts.authors['test_data'][1]['commit_cnt']
