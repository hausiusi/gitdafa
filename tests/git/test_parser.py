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


def test_stats():
    # yapf:disable - disabling to improve readability
    authors = Parse.stats(ts.stats_cmd_out).authors
    for author in authors:
        assert authors[author].name == ts.js_stats[author]['name']
        assert authors[author].email == ts.js_stats[author]['email']
        assert authors[author].lines_added == ts.js_stats[author]['lines_added']
        assert authors[author].lines_deleted == ts.js_stats[author]['lines_deleted']
    # yapf:enable
