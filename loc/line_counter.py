#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import os

from models import CodeFileInfo

"""
Leads all configuration parameters and implements the code file analyzer
 and a function for retrieving file names.
"""


def __json_load(file_path: str):
    """
    Read json file from a specified file_path
    """
    with open(file_path) as f:
        return json.load(f)


ignored = __json_load("config/ignored.json")
known_types = __json_load("config/known_types.json")


def ignored_directories_clear():
    """
    Clear ignored directories dictionary
    """
    global ignored
    ignored["directories"] = []


def ignored_subdirectories_clear():
    """
    Clear ignored subdirectories list
    """
    global ignored
    ignored["subdirectories"] = []


def ignored_extensions_clear():
    """
    Clear ignored extensions list
    """
    global ignored
    ignored["extensions"] = []


def ignored_files_clear():
    """
    Clear ignored files list
    """
    global ignored
    ignored["files"] = []


def ignored_directories_extend(directories):
    """
    Extend ignored directories list

    Parameters
    ----------
    directories : dict
    """
    global ignored
    ignored["directories"].extend(directories)


def ignored_extensions_extend(extensions):
    """
    Extend ignored extensions list

    Parameters
    ----------
    extensions : list
    """
    global ignored
    ignored["extensions"].extend(extensions)


def ignored_subdirectories_extend(subdirs):
    """
    Extend ignored_subdirectories list

    Parameters
    ----------
    subdirs : dict
    """
    global ignored
    ignored["subdirectories"].extend(subdirs)


def ignored_files_extend(files):
    """
    Extend ignored files list
    Parameters
    ----------
    files : list
    -------
    """
    global ignored
    ignored["files"].extend(files)


class LineCounter:
    """
    Analyze code and count lines

    Parameters
    ----------
    code_file_path : str
    """

    def __init__(self, code_file_path: str):
        self.code_file_path = code_file_path
        self.errors = []

    def count(self, count_continued_lines: bool) -> CodeFileInfo:
        _, ext = os.path.splitext(self.code_file_path)
        ext = ext.lower()
        comments = []
        description = "Unknown"
        language = "Unknown"
        is_source_code = False
        if ext in known_types:
            comments = known_types[ext]["comments"]
            description = known_types[ext]["description"]
            language = known_types[ext]["language"]
            is_source_code = known_types[ext]["is_source_code"]
        code_lines = 0
        comment_lines = 0
        empty_lines = 0
        comment_end = ""
        comment_end_found = True
        not_code_line = False
        try:
            for line in open(self.code_file_path, 'r', encoding='utf-8',
                             errors='replace'):
                line = line.lstrip()
                if not comment_end_found:
                    comment_lines += 1
                    if comment_end in line:
                        comment_end_found = True
                    continue
                if len(line) == 0:
                    empty_lines += 1
                    continue
                for comment in comments:
                    if len(comment) < 2:
                        msg = f'known_types.json->comments must be array of ' \
                              f'array [["start", "end"]] or empty [].' \
                              f' Check {ext}'
                        print(msg)
                        continue
                    comment_start = comment[0]
                    if line.startswith(comment_start):
                        not_code_line = True
                        comment_end = comment[1]
                        comment_lines += 1
                        # Calculate minimum expected length of the line to
                        # register the comment end
                        min_len = len(comment_start) + len(comment_end)
                        comment_end_found = (
                                comment_end in line
                                and
                                len(line) >= min_len
                        )

                if not_code_line:
                    not_code_line = False
                    continue
                if count_continued_lines or not line.endswith("\\\n"):
                    code_lines += 1

        except IOError as ex:
            msg = f"Can not open {self.code_file_path} {ex}"
            self.errors.append(msg)
        except UnicodeDecodeError as ex:
            msg = f"Failed to decode file: {self.code_file_path} {ex}"
            self.errors.append(msg)
        except Exception as ex:
            msg = f"Exception while opening and parsing {self.code_file_path} {ex}"
            self.errors.append(msg)
        else:
            return CodeFileInfo(self.code_file_path,
                                language,
                                ext,
                                comment_lines,
                                code_lines,
                                empty_lines,
                                description,
                                is_source_code)
        finally:
            for error in self.errors:
                print(f"ERROR: {error}")
        return None


def get_file_names(root_dir: str):
    """
    Get all files under the root_dir except files that are placed in the
    ignored directories or have ignored extensions

    Parameters
    ----------
    root_dir : str

    Returns
    -------
    list of str
        List of file paths
    """
    file_paths = []
    global ignored
    ignored_directories = ignored["directories"]
    ignored_extensions = ignored["extensions"]
    ignored_subdirectories = ignored["subdirectories"]
    ignored_files = ignored["files"]
    ignored_extensions = [e.lower() for e in ignored_extensions]
    if sys.platform == 'win32':
        _sep = '/'
        sep = '\\'
    else:
        _sep = '\\'
        sep = '/'
    root_dir = root_dir.replace(_sep, sep)
    ignored_directories = [igd.replace(_sep, sep) for igd in
                           ignored_directories]
    for root, _, files in os.walk(root_dir):
        check_dir = True
        split_dirs = os.path.relpath(root, root_dir).split(sep)
        for sp_dir in split_dirs:
            if sp_dir in ignored_subdirectories:
                check_dir = False
                break
        add_files = True
        if check_dir:
            for ignored_dir in ignored_directories:
                if ignored_dir in root:
                    add_files = False
                    break
            if add_files:
                for f in files:
                    if os.path.splitext(f)[-1].lower() \
                            not in ignored_extensions \
                            and f not in ignored_files:
                        file_paths.append(os.path.join(root, f))
    return file_paths
