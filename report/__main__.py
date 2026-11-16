#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generates an HTML report from an existing statistics log:

    python -m report results/<run>/stats.txt [-o output.html]
"""

import argparse

from report import generate_html_report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate an HTML report from a Gitdafa stats.txt log')
    parser.add_argument('stats_file', help='Path to the stats.txt log')
    parser.add_argument('-o', '--output', default=None,
                        help='Output HTML path (default: stats.html next to '
                             'the log)')
    args = parser.parse_args()
    print(generate_html_report(args.stats_file, args.output))
