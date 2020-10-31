#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
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
known_types = __json_load("loc/known_types.json")


def ignored_directories_clear():
    """
    Clear ignored directories dictionary
    """
    global ignored_directories
    ignored_directories = {}


def ignored_extensions_clear():
    """
    Clear ignored extensions dictionary
    """
    global ignored_extensions
    ignored_extensions = {}


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


class CodeFileAnalyzer:
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
        _, self.extension = os.path.splitext(code_file_path)
        self.code_lines = 0
        self.comment_lines = 0
        self.empty_lines = 0
        if self.extension not in known_types:
            self.type = "other"
            comments = []
        else:
            self.type = self.extension
            comments = known_types[self.type]["comments"]
        comment_end = ""
        comment_end_found = True
        self.__analyze_result_add_missing(self.type)
        try:
            for line in open(code_file_path, "r", encoding="utf-8"):
                line = line.lstrip()
                if not comment_end_found:
                    self.comment_lines += 1
                    if comment_end in line:
                        comment_end_found = True
                        continue
                if len(line) == 0:
                    self.empty_lines += 1
                    continue
                for comment in comments:
                    comment_start = comment[0]
                    if line.startswith(comment_start):
                        comment_end = comment[1]
                        self.comment_lines += 1
                        comment_end_found = False
                        # detect oneliner comments
                        if comment_end in line:
                            comment_end_found = True
                            continue
                if not comment_end_found:
                    continue
                self.code_lines += 1
        except IOError as ex:
            msg = f"Can not open {code_file_path} {ex}"
            print(msg)
            CodeFileAnalyzer.result[self.type]["errors"].append(msg)
        except UnicodeDecodeError as ex:
            msg = "Failed to decode file: {code_file_path} {ex}"
            print(msg)
            CodeFileAnalyzer.result[self.type]["errors"].append(msg)
        except Exception as ex:
            msg = f"Exception while opening and parsing {code_file_path} {ex}"
            print(msg)
            CodeFileAnalyzer.result[self.type]["errors"].append(msg)
        else:
            self.__analyze_result_update_values(self.type, self.comment_lines,
                                                self.code_lines,
                                                self.empty_lines,
                                                self.extension)

    def __analyze_result_add_missing(self, element):
        """ Adds to result dict and initializes a key when missing """
        if element in CodeFileAnalyzer.result:
            return
        CodeFileAnalyzer.result[element] = {}
        CodeFileAnalyzer.result[element]["comments"] = 0
        CodeFileAnalyzer.result[element]["code_lines"] = 0
        CodeFileAnalyzer.result[element]["empty_lines"] = 0
        CodeFileAnalyzer.result[element]["files_count"] = 0
        CodeFileAnalyzer.result[element]["types"] = []
        CodeFileAnalyzer.result[element]["errors"] = []

    def __analyze_result_update_values(self, file_type, comment_lines,
                                       code_lines, empty_lines, extension):
        CodeFileAnalyzer.result[file_type]["comments"] += comment_lines
        CodeFileAnalyzer.result[file_type]["code_lines"] += code_lines
        CodeFileAnalyzer.result[file_type]["empty_lines"] += empty_lines
        CodeFileAnalyzer.result[file_type]["files_count"] += 1
        if not extension in CodeFileAnalyzer.result[file_type]["types"]:
            CodeFileAnalyzer.result[file_type]["types"].append(extension)


def get_file_names(root_dir: str):
    """
    Get all files in specified directories
    
    Parameters
    ----------
    root_dir : str
    
    Returns
    -------
    list of str
        List of file paths
    """
    file_paths = []
    for root, _, files in os.walk(root_dir):
        continue_next = False
        for ign_dir in ignored_directories:
            extra_char = 0 if root_dir.endswith(("/", "\\")) else 1
            tmp_dir = root[len(root_dir) + extra_char:].replace("\\", "/")
            if tmp_dir.startswith(ign_dir):
                continue_next = True
                break
        if continue_next:
            continue
        for f in files:
            continue_next = False
            _, ext = os.path.splitext(f)
            if ext.lower() in ignored_extensions:
                continue_next = True
            if continue_next:
                continue
            file_paths.append(os.path.join(root, f))
    return file_paths
