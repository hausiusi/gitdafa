#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .model_interafce import TableInterface


class CodeFileInfo(TableInterface):
    def __init__(self,
                 file_path: str,
                 language: str,
                 file_ext: str,
                 comment_lines: int,
                 code_lines: int,
                 empty_lines: int,
                 description: str,
                 is_source_code: bool):
        """
        Initializes a new instance of CodeFileInfo
        @param file_path: path to the file
        @param language: programming language according to extension
        otherwise use some common word for every instance e.g. "other"
        @param file_ext: file extension
        @param code_lines: count of the code lines in the file
        @param comment_lines: count of the comment lines in the file
        @param empty_lines: count of the empty lines in the file
        @param description: file description according to its extension
        @param is_source_code: whether file is a source code or a text
        """
        self.file_path: str = file_path
        self.language: str = language
        self.file_ext: str = file_ext
        self.code_lines: int = code_lines
        self.comment_lines: int = comment_lines
        self.empty_lines: int = empty_lines
        self.description: str = description
        self.is_source_code: bool = is_source_code

    def get_table_row(self) -> []:
        return [self.file_path,
                self.file_ext,
                self.language,
                self.code_lines,
                self.comment_lines,
                self.empty_lines]

    def get_table_headers(self) -> []:
        return ["File name",
                "Extension",
                "Language",
                "Code lines",
                "Comment lines",
                "Empty lines"]
