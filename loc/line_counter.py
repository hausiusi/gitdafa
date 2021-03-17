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


ignored_directories = __json_load("loc/ignored_directories.json")
ignored_extensions = __json_load("loc/ignored_extensions.json")
ignored_subdirs = __json_load("loc/ignored_subdirs.json")
known_types = __json_load("loc/known_types.json")


def ignored_directories_clear():
    """
    Clear ignored directories dictionary
    """
    global ignored_directories
    ignored_directories = []

def ignored_subdirectories_clear():
    """
    Clear ignored subdirs dictionary
    """
    global ignored_subdirs
    ignored_subdirs = []

def ignored_extensions_clear():
    """
    Clear ignored extensions dictionary
    """
    global ignored_extensions
    ignored_extensions = []


def ignored_directories_extend(directories):
    """
    Extend ignored_directories dictionary
    
    Parameters
    ----------
    directories : dict
    """
    global ignored_directories
    ignored_directories.extend(directories)


def ignored_extensions_extend(extensions):
    """
    Extend ignored_extensions dictionary
    
    Parameters
    ----------
    extensions : dict
    """
    global ignored_extensions
    ignored_extensions.extend(extensions)


def ignored_subdirectories_extend(subdirs):
    """
    Extend ignored_subdirs dictionary
    
    Parameters
    ----------
    subdirs : dict
    """
    global ignored_subdirs
    ignored_subdirs.extend(subdirs)


class LineCounter:
    """
    Analyze code in file
    
    Parameters
    ----------
    code_file_path : str
    
    Class Attributes
    ---------------
    result : dict
        Dictionary for storing CodeFileAnalyzer results

    Attributes
    ----------
    extension : str
        Code file extension
    code_lines : int
        Code line count
    comment_lines : int
        Comment line count
    empty_lines : int
        Empty line count

    """
    result = {}

    def __init__(self, code_file_path: str):
        self.code_file_path = code_file_path
        self.errors = []

    def count(self) -> CodeFileInfo:
        _, ext = os.path.splitext(self.code_file_path)
        ext = ext.lower()
        file_type = "other"
        comments = []
        description = "Unknown"
        language = "Unknown"
        if ext in known_types:
            file_type = ext
            comments = known_types[file_type]["comments"]
            description = known_types[file_type]["description"]
            language = known_types[file_type]["language"]
        code_lines = 0
        comment_lines = 0
        empty_lines = 0
        comment_end = ""
        comment_end_found = True
        not_code_line = False
        try:
            for line in open(self.code_file_path, 'r', encoding='utf-8', errors='replace'):
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
                    if (len(comment)) < 2:
                        msg = f'known_types.json->comments must be array of array [["start", "end"]] or empty [].' \
                              f' Check {ext}'
                        print(msg)
                        continue
                    comment_start = comment[0]
                    if line.startswith(comment_start):
                        comment_end = comment[1]
                        comment_lines += 1
                        comment_end_found = comment_end in line
                        not_code_line = True
                if not_code_line:
                    not_code_line = False
                    continue
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
                                file_type,
                                comment_lines,
                                code_lines,
                                empty_lines,
                                description)
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
    global ignored_extensions
    global ignored_directories 
    ignored_extensions = [e.lower() for e in ignored_extensions]
    if sys.platform == 'win32':
        _sep = '/'
        sep = '\\'
    else:
        _sep = '\\'
        sep = '/'
    root_dir = root_dir.replace(_sep, sep)
    ignored_directories = [igd.replace(_sep, sep) for igd in ignored_directories]
    for root, _, files in os.walk(root_dir):
        check_dir = True
        split_dirs = os.path.relpath(root, root_dir).split(sep)
        for sp_dir in split_dirs:
            if sp_dir in ignored_subdirs:
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
                    if os.path.splitext(f)[-1].lower() not in ignored_extensions:
                        file_paths.append(os.path.join(root, f))
    return file_paths
