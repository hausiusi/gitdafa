#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmd_runner import CmdOutput, CmdRunner
from models import Statistics
from models import Author
import argparse
import os

# help
EPILOG = """\
Gitribution is a tool intended for statistical analyzes of git projects.S
"""
runner = CmdRunner()
stats = Statistics()


def get_commits_by_authors():
    result = runner.run("git shortlog -s")
    output = result.stdout.split("\n")
    for line in output:
        parts = line.split("\t")
        if len(parts) > 1:
            author = Author()
            author.commits_count = parts[0]
            author.name = parts[1]
            stats.authors.append(author)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    # yapf:disable - disabling formatting while apprending parser arguments to improve readability
    parser.add_argument("-p", "--projdir", metavar="", help="Path to project root directory", default="./")

    # yapf: enable

    args = parser.parse_args()
    saved_working_dir = os.getcwd()
    os.chdir(args.projdir)
    get_commits_by_authors()
    for aut in stats.authors:
        print(f"Author: {aut.name} - {aut.commits_count} commits")

    # change working directory back to saved one
    os.chdir(saved_working_dir)
