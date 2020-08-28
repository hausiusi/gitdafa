#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmd_runner import CmdOutput, CmdRunner
from models import Statistics
from models import Author
from models import Change
from models import Commit
import datetime
import argparse
import os

# help
EPILOG = """\
Gitribution is a tool intended for statistical analyzes of git projects.S
"""
runner = CmdRunner()
stats = Statistics()

CMD_LOG = "git log --pretty=oneline"
CMD_SHOW = "git show --stat {commit}"
CMD_SHOW_ALL = "git show --stat -1000000"
CMD_SHORTLOG = "git shortlog -s"
CMD_LOG_STAT = "git log --stat"
CMD_LOG_NUMSTAT = "git log --numstat"


def get_author(lines):
    name = None
    email = None
    for line in lines:
        if line[:8] == "Author: ":
            data = line[8:].split(" <")
            name = data[0]
            email = data[1][:-1]
            break
    return Author(name=name, email=email)


def get_date(lines):
    for line in lines:
        if line[:6] == "Date: ":
            date = datetime.datetime.strptime(line[6:].strip(),
                                              '%a %b %d %H:%M:%S %Y %z')
            return date


def get_message(lines):
    after_date = False
    empty_count = 0
    message = ""
    for line in lines:
        if after_date:
            message += line + '\n'
            if len(line) == 0:
                empty_count += 1
            if empty_count == 2:
                return message
        if line[:6] == "Date: ":
            after_date = True
            continue


def __get_file_change(file_text):
    try:
        data = file_text.split()
        file_name = data[2].strip()
        added, deleted = 0, 0
        if data[0].strip() != '-':
            added = int(data[0].strip())
        if data[1].strip() != '-':
            deleted = int(data[1].strip())
        return Change(file_name=file_name, added=added, deleted=deleted)
    except Exception as ex:
        print(f"{ex} Error happened douring parsing a commit data")


def get_changes(lines):
    after_date = False
    after_message = False
    empty_count = 0
    changes = []
    for line in lines[:-1]:
        if after_message:
            changes.append(__get_file_change(line))
        if after_date:
            if len(line) == 0:
                empty_count += 1
            if empty_count == 2:
                after_message = True
        if line[:6] == "Date: ":
            after_date = True
            continue
    return changes


def get_commits_by_authors():
    result = runner.run(CMD_SHORTLOG)
    output = result.stdout.split("\n")
    for line in output:
        parts = line.split("\t")
        if len(parts) > 1:
            author = Author()
            author.commits_count = parts[0]
            author.name = parts[1]
            stats.authors.append(author)


def get_stats():
    runner = CmdRunner()
    result = runner.run(CMD_LOG_NUMSTAT)
    commit_texts = result.stdout.split("\ncommit ")

    for commit_text in commit_texts:
        commit_lines = commit_text.split('\n')
        commit_id = commit_lines[0].strip()
        commit = Commit(commit_id)
        date = get_date(commit_lines)
        commit.date = str(date)
        commit.message = get_message(commit_lines)

        commit.changes = get_changes(commit_lines)
        author = get_author(commit_lines)

        if author.email not in stats.authors:
            stats.authors[author.email] = author

        stats.authors[author.email].add_commit(commit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    # yapf:disable - disabling formatting while apprending parser arguments to improve readability
    parser.add_argument("-p", "--projdir", metavar="", help="Path to project root directory", default="./")

    # yapf: enable

    args = parser.parse_args()
    saved_working_dir = os.getcwd()
    os.chdir(args.projdir)

    get_stats()
    for aut in stats.authors:
        print(f"Author: {stats.authors[aut].name} - " + \
              f"{stats.authors[aut].commits_count} commits" + \
                  f" {stats.authors[aut].lines_added} lines added" + \
                      f" {stats.authors[aut].lines_deleted} lines deleted")

    # change working directory back to saved one
    os.chdir(saved_working_dir)
