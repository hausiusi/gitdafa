#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .model_interafce import TableInterface
from .code_file_info import CodeFileInfo


class LanguageStats(TableInterface):
    def __init__(self, language: str):
        self.code_file_info_lst: CodeFileInfo = []
        self.language: str = language
        self.code_lines: int = 0
        self.comment_lines: int = 0
        self.empty_lines: int = 0
        self.files_count: int = 0

    def add_code_file_info(self, code_file_info: CodeFileInfo):
        """
        Adds a reference to the new CodeFileInfo instance of the same language
        to the list `code_file_info_lst` and adds the count of code/comment/empty
        lines to the corresponding attributes
        @param code_file_info: Instance of CodeFileInfo that has the same self.language
        as this object

        @Note In case of different languages ERROR message will be printed and adding
        process will be skipped
        @return: None
        """
        if code_file_info.language != self.language:
            print(f'\n\nERROR: File "{code_file_info.file_path}" '
                  f'language "{code_file_info.language}" must match with'
                  f'destination language "{self.language}"')
            return
        self.code_file_info_lst.append(code_file_info)
        self.code_lines += code_file_info.code_lines
        self.comment_lines += code_file_info.comment_lines
        self.empty_lines += code_file_info.empty_lines
        self.files_count += 1

    def get_table_row(self) -> []:
        return [self.language,
                self.code_lines,
                self.comment_lines,
                self.empty_lines,
                self.files_count]

    def get_table_headers(self) -> []:
        return ["Language",
                "Code lines",
                "Comment lines",
                "Empty lines",
                "Files count"]