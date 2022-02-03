#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from datetime import datetime
from os import path

import loc
from census import Statistics

# help
EPILOG = """\
Gitribution is a tool intended for statistical analyzes of git projects.
"""


def save_results(results_file: str, time_start, time_end,
                 statistics: Statistics):
    elapsed = time_end - time_start
    data_to_write = f"Duration: {str(elapsed)}\n\n{str(statistics)}"
    with open(results_file, encoding="utf-8", mode="w", errors='replace') as f:
        f.write(data_to_write)


def prepare_results_file(root_dir: str, start_time: datetime) -> str:
    results_dir = root_dir + "/results/"
    proj_name = path.basename(args.projdir.strip('/').strip('\\'))
    results_file = f'{results_dir}{start_time.strftime("%Y-%m-%d-%H-%M-%S")}_{proj_name}/stats.txt'
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    return results_file


def prepare_for_statistics(root_dir,
                           commits_per_step,
                           count_continued_lines) -> Statistics:
    statistics = Statistics(root_dir, commits_per_step,
                            count_continued_lines=count_continued_lines)
    request_map = {
        'authors': statistics.parse_authors,
        'authors_per_month': statistics.parse_authors_per_month,
        'tags': statistics.parse_tags,
        'loc': statistics.count_lines
    }
    return statistics, request_map


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-pd',
                        '--projdir',
                        metavar='',
                        help='Path to project root directory',
                        default="./")
    parser.add_argument('-id',
                        '--igndir',
                        metavar='',
                        help='Appends directories that will be ignored',
                        default=[],
                        nargs="+")
    parser.add_argument('-ie',
                        "--ignext",
                        metavar='',
                        help="Appends extensions that will be ignored",
                        default=[],
                        nargs="+")
    parser.add_argument('-if',
                        "--ignfiles",
                        metavar='',
                        help="Appends files that will be ignored",
                        default=[],
                        nargs="+")
    parser.add_argument('-idc',
                        '--igndir_clear',
                        metavar='',
                        help='Resets default directories that will be ignored',
                        default=False)
    parser.add_argument('-iec',
                        '--ignext_clear',
                        metavar='',
                        help='Resets default extensions that will be ignored',
                        default=False)
    parser.add_argument('-ccl',
                        '--count_continued_lines',
                        help='When set, the lines which end with \\ symbol '
                             'will be counted as a code line, otherwise, '
                             '\\ ending lines will be ignored',
                        action='store_true')
    parser.add_argument('-cps',
                        '--commits_per_step',
                        metavar='',
                        help='Retrieved and parsed commits per step',
                        default=20000)
    parser.add_argument('-s',
                        '--stats',
                        metavar='',
                        help='Creates desired statistics '
                             '(authors, authors_per_month, tags, loc)',
                        default=['all'],
                        nargs="+")

    t_start = datetime.now()
    args = parser.parse_args()
    main_script_dir = sys.path[0]
    res_file = prepare_results_file(main_script_dir, t_start)
    os.chdir(args.projdir)
    if args.igndir_clear:
        loc.ignored_directories_clear()
    if args.ignext_clear:
        loc.ignored_extensions_clear()

    loc.ignored_directories_extend(args.igndir)
    loc.ignored_extensions_extend(args.ignext)
    loc.ignored_files_extend(args.ignfiles)

    stats, fn_map = prepare_for_statistics(args.projdir,
                                           args.commits_per_step,
                                           args.count_continued_lines)

    if "all" in args.stats:
        for k in fn_map.keys():
            fn_map[k]()
    else:
        for req in args.stats:
            fn_map[req]()

    print(stats)
    save_results(res_file, t_start, datetime.now(), stats)
    # change working directory back to the initial one
    os.chdir(main_script_dir)
