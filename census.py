#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from _cmd import CmdRunner
from git import Parse
from git import Cmd
from models import Commit, LanguageStats
from models import Tag
from string import Formatter
from tabulate import tabulate
import re
from datetime import datetime
from loc import line_counter
from loc.line_counter import LineCounter


class Statistics(object):
    """
    Takes care of all types of statistical analysis
    """

    def __init__(self,
                 root_dir,
                 parse_step_len: int = 20000,
                 count_continued_lines: bool = False,
                 runner=CmdRunner):
        self.runner = runner
        self.authors = AuthorsCollection()
        self.tags = TagsCollection()
        self.language_stats = LanguageStatsCollection()
        self.code_file_infos = CodeFileInfoCollection()
        self.branch: str = self.runner.run(Cmd.CURRENT_BRANCH).stdout
        self.commits_count: int = int(
            self.runner.run(Cmd.COMMIT_COUNT_BRANCH).stdout)
        self.first_commit_date = self.runner.run(Cmd.FIRST_COMMIT_DATE).stdout
        self.last_commit_date = self.runner.run(Cmd.LAST_COMMIT_DATE).stdout
        self.parse_step_len: int = int(parse_step_len)
        self.root_dir: str = root_dir
        self.count_continued_lines = count_continued_lines
        self.errors: list = []

    def parse_authors(self):
        self.authors.collection_creation_start()
        for i in range(0, self.commits_count, self.parse_step_len):
            current_step = min(self.parse_step_len, self.commits_count - i)
            cmd_output = self.runner.run(Cmd.LOG_NUMSTAT_SKIP_X_GET_Y %
                                         (i, current_step))
            commit_texts = cmd_output.stdout.split("\ncommit ")
            for commit_text in commit_texts:
                commit_id = Parse.commit_id(commit_text)
                commit_ = Commit(commit_id)
                date = Parse.date(commit_text)
                commit_.date = str(date)
                commit_.message = Parse.message(commit_text)
                commit_.changes = Parse.changes(commit_text)
                author_ = Parse.author(commit_text)
                if author_ is None:
                    print(
                        '\n\nERROR: Could not parse commit text\n'
                        f'Sometimes it happens when commits per step is little (CURRENT: {self.parse_step_len}). '
                        f'Try to increase it at least to 500\n'
                        f'Also, please try to run this command manually: "{cmd_output.cmd}"\n'
                        f'COMMIT TEXT:\n{commit_text}\n------------\n')
                    raise IOError

                if author_.email not in self.authors.collection:
                    self.authors.collection[author_.email] = author_

                self.authors.collection[author_.email].add_commit(commit_)

            percents = self.__get_progress_in_percents(i, current_step,
                                                       self.commits_count)
            progress = f"{current_step + i}/{self.commits_count} commits parsed ({percents}%)"
            print(progress, end='\r')
        self.authors.collection_creation_end()
        return self

    def parse_tags(self):
        self.tags.collection_creation_start()
        cmd_output = self.runner.run(Cmd.TAGS)
        tag_lines = cmd_output.stdout.splitlines()
        if len(tag_lines) == 1:
            pass

        all_sha = "000000\n" + self.runner.run(Cmd.SHA_LIST_REVERSED).stdout
        tag_id = 0
        # take the first our custom commit sha in the beginning
        previous_tag_commit_sha = all_sha[:all_sha.index('\n')]
        for line in tag_lines:
            name = line
            sha = self.runner.run(Cmd.REV_PARSE % name).stdout
            matches = re.findall(f'{previous_tag_commit_sha}.*{sha}', all_sha,
                                 re.DOTALL)
            if len(matches) == 0:
                # sometimes next tag is not among next commits, reverse the search range
                matches = re.findall(f'{sha}.*{previous_tag_commit_sha}',
                                     all_sha, re.DOTALL)
            if len(matches) == 0:
                branch_containing_tag = self.runner.run(
                    Cmd.BRANCH_TAG_CONTAINS % name, exit_on_fail=False).stdout
                if branch_containing_tag == "":
                    print(f'ERROR: TAG {name} couldn\'t find on any branch')
                    continue

                print(
                    f"WARNING: TAG {name} with SHA1 {sha} found on branch {branch_containing_tag}"
                )
                continue
            # dropping the first sha1 as it can be our custom or sha1 from the previous tag
            tag_sha_list = matches[0].split("\n")[1:]
            previous_tag_commit_sha = tag_sha_list[-1]
            tag_ = Tag(sha, name, tag_sha_list, tag_id)
            self.tags.collection[tag_.name] = tag_
            tag_id += 1
        self.tags.collection_creation_end()
        return self

    def parse_contribution_in_current_code(self):

        return self

    def count_lines(self):
        self.language_stats.collection_creation_start()
        files_to_analyze = line_counter.get_file_names(self.root_dir)
        files_count = len(files_to_analyze)
        current = 0
        for file in files_to_analyze:
            current += 1
            cf_analyzer = LineCounter(file)
            cfi = cf_analyzer.count(self.count_continued_lines)
            if cfi is None:
                self.errors.extend(cf_analyzer.errors)
                continue
            if cfi.language not in self.language_stats.collection.keys():
                self.language_stats.collection[cfi.language] = LanguageStats(
                    cfi.language)
            self.code_file_infos.collection[cfi.file_path] = cfi
            self.language_stats.collection[cfi.language].add_code_file_info(
                cfi)
            percents = self.__get_progress_in_percents(0, current, files_count)
            print(f'{current}/{files_count} files checked ({percents}%)',
                  end='\r')

        self.language_stats.collection_creation_end()
        return self

    @classmethod
    def __get_table(cls, _dict):
        rows = []
        if len(_dict.keys()) == 0:
            return "N/A"
        for k in _dict.keys():
            rows.append(_dict[k].get_table_row())
        headers = next(iter(_dict.values())).get_table_headers()
        table = tabulate(rows, headers)
        return table

    @staticmethod
    def __get_progress_in_percents(base, current, total):
        current += base
        ratio = current / total
        percents = round(ratio * 100, 1)
        return min(percents, 100)

    def __str__(self):
        authors = self.authors.collection
        authors_duration = self.authors.collection_creation_duration(
            '{H:02}:{M:02}:{S:02}.{F:06}')
        tags = self.tags.collection
        tags_duration = self.tags.collection_creation_duration(
            '{H:02}:{M:02}:{S:02}.{F:06}')
        lang_stats = self.language_stats.collection
        lang_stats_duration = self.language_stats.collection_creation_duration(
            '{H:02}:{M:02}:{S:02}.{F:06}')
        code_file_infos = self.code_file_infos.collection

        authors_table = self.__get_table(authors)
        tags_table = self.__get_table(tags)
        lang_stats_table = self.__get_table(lang_stats)
        analyzed_files_table = self.__get_table(code_file_infos)
        project_duration = datetime.strptime(
            self.last_commit_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(
            self.first_commit_date, '%Y-%m-%d %H:%M:%S')

        ret = \
            f'\n\nSTATISTICS\nBranch: {self.branch}\nAll commits: {self.commits_count}' \
            f'\nTotal days: {project_duration.days}' \
            f'\n\nAUTHORS({len(authors)})\n{authors_table}\nDuration: {authors_duration}' \
            f'\n\nTAGS({len(tags)})\n{tags_table}\nDuration: {tags_duration}' \
            f'\n\nLOC({len(lang_stats)} language types)\n{lang_stats_table}\nDuration: {lang_stats_duration}' \
            f'\n\nAnalyzed {len(code_file_infos)} different files\n{analyzed_files_table}' \
            f'\n\nERRORS {self.errors}'
        return ret

    def __repr__(self):
        return f'{self.authors.collection} {self.tags.collection} {self.language_stats.collection}'


class TimedCollectionBase:
    def __init__(self, collection_name: str):
        self.ts: datetime = datetime.now()
        self.te: datetime = datetime.now()
        self.collection: dict = {}
        self.collection_name = collection_name

    def collection_creation_start(self):
        self.ts = datetime.now()

    def collection_creation_end(self):
        self.te = datetime.now()

    def collection_creation_duration(
            self, fmt='{D:03}d {H:02}h {M:02}m {S:02}s {F:06}us'):
        elapsed = self.te - self.ts
        remainder = elapsed.total_seconds()
        f = Formatter()
        desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
        possible_fields = ('W', 'D', 'H', 'M', 'S', 'F')
        constants = {
            'W': 604800,
            'D': 86400,
            'H': 3600,
            'M': 60,
            'S': 1,
            'F': 0.000001
        }
        values = {}
        for field in possible_fields:
            if field in desired_fields and field in constants:
                value, remainder = divmod(remainder, constants[field])
                values[field] = int(value)
        return f.format(fmt, **values)


class AuthorsCollection(TimedCollectionBase):
    def __init__(self):
        super().__init__('Authors')


class TagsCollection(TimedCollectionBase):
    def __init__(self):
        super().__init__('Tags')


class LanguageStatsCollection(TimedCollectionBase):
    def __init__(self):
        super().__init__('LanguageStats')

    def collection_creation_end(self):
        total_lines = 0
        total_code = 0
        total_code_comments = 0
        for language in self.collection:
            lang = self.collection[language]
            total_lines += lang.code_lines + \
                           lang.comment_lines + \
                           lang.empty_lines + \
                           lang.text_lines
            total_code += lang.code_lines
            total_code_comments += lang.code_lines + lang.comment_lines

        for language in self.collection:
            lang = self.collection[language]
            lang.ratio_code = self.__get_ratio_in_percents(
                lang.code_lines, total_code)
            lang.ratio_code_comments = self.__get_ratio_in_percents(
                lang.code_lines + lang.comment_lines, total_code_comments)
            lang.ratio_total_lines = self.__get_ratio_in_percents(
                lang.code_lines + lang.comment_lines + lang.empty_lines +
                lang.text_lines, total_lines)
        super().collection_creation_end()

    @staticmethod
    def __get_ratio_in_percents(current, total, precision=3):
        ratio = current / total
        percents = round(ratio * 100, precision)
        return min(percents, 100)


class CodeFileInfoCollection(TimedCollectionBase):
    def __init__(self):
        super().__init__('CodeFileInfo')
