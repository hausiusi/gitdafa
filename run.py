#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import ntpath
import os
from datetime import datetime

import loc
from git import Statistics

# help
EPILOG = """\
Gitribution is a tool intended for statistical analyzes of git projects.
"""


def save_results(root_dir: str, statistics: Statistics):
    results_dir = root_dir + "/results/"
    results_file = f'{results_dir}{t_start.strftime("%Y-%m-%d-%H-%M-%S")}_{ntpath.basename(args.projdir)}/stats.txt'
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    with open(results_file, encoding="utf-8", mode="w", errors='replace') as f:
        f.write(str(statistics))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    # yapf:disable - disabling formatting while apprending parser arguments to improve readability
    parser.add_argument('-p', '--projdir', metavar='', help='Path to project root directory', default="./")
    parser.add_argument("-id", '--igndir', metavar='', help='Appends directories that will be ignored', default=[], nargs="+")
    parser.add_argument('-ie', "--ignext", metavar='', help="Appends extensions that will be ignored", default=[], nargs="+")
    parser.add_argument('-idc', '--igndir_clear', metavar='', help='Resets default directories that will be ignored', default=False)
    parser.add_argument('-iec', '--ignext_clear', metavar='', help='Resets default extensions that will be ignored', default=False)
    parser.add_argument('-cps', '--commits_per_step', metavar='', help='Retrieved and parsed commits per step', default=20000)

    # yapf:enable
    t_start = datetime.now()
    args = parser.parse_args()
    saved_working_dir = os.getcwd()
    os.chdir(args.projdir)
    if args.igndir_clear:
        loc.ignored_directories_clear()
    if args.ignext_clear:
        loc.ignored_extensions_clear

    loc.ignored_directories_extend(args.igndir)
    loc.ignored_extensions_extend(args.ignext)

    stats = Statistics(args.commits_per_step).parse_authors()
    print(stats)
    save_results(saved_working_dir, stats)
    exit(0)
    file_paths = loc.get_file_names(args.projdir)
    for f in file_paths:
        result = loc.CodeFileAnalyzer(f)
        print(f"File: {f} code: {result.code_lines},"
              f"comments: {result.comment_lines}, empty: " \
              f"{result.empty_lines}")

    print(loc.CodeFileAnalyzer.result)
    # change working directory back to saved one
    os.chdir(saved_working_dir)
