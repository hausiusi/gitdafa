#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from models import Statistics
from models import Author
from models import Change
from models import Commit
from git import Cmd
from git import CmdRunner
from git import Parse
import loc
import datetime
import argparse
import os

# help
EPILOG = """\
Gitribution is a tool intended for statistical analyzes of git projects.
"""


def get_commits_by_authors():
    result = CmdRunner.run(Cmd.SHORTLOG)
    return Parse.commits_by_authors(result)


def get_stats():
    result = CmdRunner.run(Cmd.LOG_NUMSTAT)
    return Parse.stats(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    # yapf:disable - disabling formatting while apprending parser arguments to improve readability
    parser.add_argument("-p", "--projdir", metavar="", help="Path to project root directory", default="./")
    parser.add_argument("-d", "--igndir", metavar="", help="Appends directories that will be ignored", default=[], nargs="+")
    parser.add_argument("-e", "--ignext", metavar="", help="Appends extensions that will be ignored", default=[], nargs="+")
    parser.add_argument("--igndir_clear", metavar="", help="Resets default directories that will be ignored", default=False)
    parser.add_argument("--ignext_clear", metavar="", help="Resets default extensions that will be ignored", default=False)

    # yapf:enable

    args = parser.parse_args()
    saved_working_dir = os.getcwd()
    os.chdir(args.projdir)
    if args.igndir_clear:
        loc.ignored_directories_clear()
    if args.ignext_clear:
        loc.ignored_extensions_clear

    loc.ignored_directories_extend(args.igndir)
    loc.ignored_extensions_extend(args.ignext)

    stats = get_stats()
    for aut in stats.authors:
        print(f"Author: {stats.authors[aut].name} - " \
              f"{stats.authors[aut].commits_count} commits" \
              f" {stats.authors[aut].lines_added} lines added" \
              f" {stats.authors[aut].lines_deleted} lines deleted")
        pass
    file_paths = loc.get_file_names(args.projdir)
    for f in file_paths:
        result = loc.CodeFileAnalyzer(f)
        print(f"File: {f} code: {result.code_lines},"
              f"comments: {result.comment_lines}, empty: " \
              f"{result.empty_lines}")

    print(loc.CodeFileAnalyzer.result)
    # change working directory back to saved one
    os.chdir(saved_working_dir)
