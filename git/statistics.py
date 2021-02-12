#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from git import *
from models import *
from tabulate import tabulate
import re
from datetime import datetime


class Statistics(object):
    """
    Model currently implements only a attribute with type dictionary of Author's
    """

    def __init__(self, parse_step_len: int = 20000):
        self.authors: dict = {}
        self.tags: dict = {}
        self.branch: str = CmdRunner.run(Cmd.CURRENT_BRANCH).stdout
        self.commits_count: int = int(CmdRunner.run(Cmd.COMMIT_COUNT).stdout)
        self.parse_step_len: int = int(parse_step_len)

    def parse_authors(self):
        for i in range(0, self.commits_count, self.parse_step_len):
            ts = datetime.now()
            cmd_output = CmdRunner.run(Cmd.LOG_NUMSTAT_SKIP_X_GET_Y %
                                       (i, self.parse_step_len))
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
                    print("\n\nERROR: Couldn't parse commit text\n"
                          f"Sometimes is happens when commits per step is little (CURRENT: {self.parse_step_len}). "
                          f"Try to increase it at least to 500\n"
                          f"Also, please try to run this command manually: {cmd_output.cmd}\n"
                          f"COMMIT TEXT:\n{commit_text}\n------------\n")
                    raise IOError

                if author_.email not in self.authors:
                    self.authors[author_.email] = author_

                self.authors[author_.email].add_commit(commit_)

            percents = min(
                round(((i + self.parse_step_len) / self.commits_count) * 100,
                      1), 100)
            te = datetime.now() - ts
            total_seconds = round(te.total_seconds(), 3)
            progress = f"Parsed commits from {i} to {self.parse_step_len + i} ({percents}%) {total_seconds}seconds"
            print(progress)
        return self

    def parse_tags(self):
        cmd_output = CmdRunner.run(Cmd.TAGS)
        tag_lines = cmd_output.stdout.split("\n")
        if len(tag_lines) == 0:
            pass

        all_sha = "000000\n" + CmdRunner.run(Cmd.SHA_LIST_REVERSED).stdout
        tag_id = 0
        # take the first our custom commit sha in the beginning
        previous_tag_commit_sha = all_sha[:all_sha.index("\n")]
        for line in tag_lines:
            name = line
            sha = CmdRunner.run(Cmd.REV_PARSE % name).stdout
            matches = re.findall(f"{previous_tag_commit_sha}.*{sha}", all_sha,
                                 re.DOTALL)
            if len(matches) == 0:
                # sometimes next tag is not among next commits, reverse the search range
                matches = re.findall(f"{sha}.*{previous_tag_commit_sha}",
                                     all_sha, re.DOTALL)
            if len(matches) == 0:
                branch_containing_tag = CmdRunner.run(
                    Cmd.BRANCH_TAG_CONTAINS % name, exit_on_fail=False).stdout
                if branch_containing_tag == "":
                    print(f"ERROR: TAG {name} couldn't find on any branch")
                    continue

                print(
                    f"WARNING: TAG {name} with SHA1 {sha} found on branch {branch_containing_tag}"
                )
                continue
            # dropping the first sha1 as it can be our custom or sha1 from the previous tag
            tag_sha_list = matches[0].split("\n")[1:]
            previous_tag_commit_sha = tag_sha_list[-1]
            tag_ = Tag(sha, name, tag_sha_list, tag_id)
            self.tags[tag_.name] = tag_
            tag_id += 1
        return self

    def parse_contribution_in_current_code(self):

        return self

    @classmethod
    def __get_table(cls, _dict):
        rows = []
        if len(_dict.keys()) == 0:
            return "N/A"
        for k in _dict.keys():
            rows.append(_dict[k].get_table_row())
        table = tabulate(rows, _dict[k].get_table_headers())
        return table

    def __str__(self):
        authors_table = self.__get_table(self.authors)
        tags_table = self.__get_table(self.tags)

        return f"\n\nSTATISTICS\nBranch: {self.branch}\nAll commits: {self.commits_count}" \
               f"\n\nAUTHORS({len(self.authors)})\n{authors_table}" \
               f"\n\nTAGS({len(self.tags)})\n{tags_table}\n"

    def __repr__(self):
        return str(self.authors)
