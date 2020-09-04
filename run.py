#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models import Statistics
from models import Author
from models import Change
from models import Commit
from git import Cmd
from git import CmdRunner
from git import Parse
import datetime
import argparse
import os

# help
EPILOG = """\
Gitribution is a tool intended for statistical analyzes of git projects.
"""


def get_commits_by_authors():
    result = CmdRunner.run(Cmd.SHORTLOG)
    return Parse.commits_by_author(result)


def get_stats():
    result = CmdRunner.run(Cmd.LOG_NUMSTAT)
    return Parse.stats(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    # yapf:disable - disabling formatting while apprending parser arguments to improve readability
    parser.add_argument("-p", "--projdir", metavar="", help="Path to project root directory", default="./")

    # yapf:enable

    args = parser.parse_args()
    saved_working_dir = os.getcwd()
    os.chdir(args.projdir)

    stats = get_stats()
    for aut in stats.authors:
        print(f"Author: {stats.authors[aut].name} - " + \
              f"{stats.authors[aut].commits_count} commits" + \
                  f" {stats.authors[aut].lines_added} lines added" + \
                      f" {stats.authors[aut].lines_deleted} lines deleted")

    # change working directory back to saved one
    os.chdir(saved_working_dir)
