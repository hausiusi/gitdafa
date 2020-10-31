from models import Statistics
from models import Commit
from models import Author
from models import Change
import datetime
"""
Docstring for parser module

The parser module contains the Parse class and methods for parsing various parts 
of git command response messages.
"""


class Parse:
    """
    Git command response parsing class
    
    Methods
    -------
    author(lines)
        Get author of the commit
    date(lines)
        Get date from commit
    message(lines)
        Get commit message
    changes(lines)
       Get count of the line change in committed files
    commits_by_authors(cmd_output)
       Get all authors of all commits
    stats(cmd_output)
        Get authors and their commits

    Notes
    -----
    Class has privete helper method __get_file_change which counts file changes.
    """
    @classmethod
    def author(cls, lines):
        """
        Get author of the commit.
        
        Parameters
        ----------
        lines : list of str
            Represents all data lines in a one commit message.
        
        Returns
        -------
        Author 
            Commit author object
        """
        name = None
        email = None
        for line in lines:
            if line[:8] == "Author: ":
                data = line[8:].split(" <")
                name = data[0]
                email = data[1][:-1]
                break
        return Author(name=name, email=email)

    @classmethod
    def date(cls, lines: list):
        """
        Get data of the commits.

        Parameters
        ----------
        lines : list of str
            Represents all data lines in a one commit message.
        
        Returns
        -------
        datetime.datetime
            Commit date
        """
        for line in lines:
            if line[:6] == "Date: ":
                date = datetime.datetime.strptime(line[6:].strip(),
                                                  '%a %b %d %H:%M:%S %Y %z')
                return date

    @classmethod
    def message(cls, lines: list):
        """
        Get commit message 
        
        Parameters
        ----------
        lines : list of str
            Represents all data lines in a one commit message.
        
        Returns
        -------
        str
            Message string
        """
        after_date = False
        empty_count = 0
        message = ""
        for line in lines:
            if after_date:
                message += line + '\n'
                if len(line) == 0:
                    empty_count += 1
                if empty_count == 2:
                    return message
            if line[:6] == "Date: ":
                after_date = True
                continue

    @classmethod
    def __get_file_change(cls, file_text):
        """
        Get count of the line change in one file.
        
        Parameters
        ----------
        file_text : str
            Represents file change info with ++ and -- signs.
        
        Returns
        -------
        Change
            One file change object

        """
        data = file_text.split()
        file_name = data[2].strip()
        added, deleted = 0, 0
        if data[0].strip() != '-':
            added = int(data[0].strip())
        if data[1].strip() != '-':
            deleted = int(data[1].strip())
        return Change(file_name=file_name, added=added, deleted=deleted)

    @classmethod
    def changes(cls, lines: list):
        """
        Get count of the line change in committed files
        
        Parameters
        ----------
        lines : list of str
            Represents all data lines in a one commit message.
        
        Returns
        -------
        list of Change
            Changes in commit
        """
        after_date = False
        after_message = False
        empty_count = 0
        changes = []
        for line in lines[:-1]:
            if after_message:
                changes.append(cls.__get_file_change(line))
            if after_date:
                if len(line) == 0:
                    empty_count += 1
                if empty_count == 2:
                    after_message = True
            if line[:6] == "Date: ":
                after_date = True
                continue
        return changes

    @classmethod
    def commits_by_authors(cls, cmd_output):
        """
        Get all authors of all commits
        
        Parameters
        ----------
        cmd_output : CmdOutput
        
        Returns
        -------
        list of Author
        """
        output = cmd_output.stdout.split("\n")
        authors = []
        for line in output:
            parts = line.split("\t")
            if len(parts) > 1:
                author = Author()
                author.commits_count = parts[0]
                author.name = parts[1]
                authors.append(author)
        return authors

    @classmethod
    def stats(cls, cmd_output):
        """
        Get authors and their commits
        
        Parameters
        ----------
        cmd_output : CmdOutput

        Returns
        -------
        Statistics
        """
        stats = Statistics()
        commit_texts = cmd_output.stdout.split("\ncommit ")

        for commit_text in commit_texts:
            commit_lines = commit_text.split('\n')
            commit_id = commit_lines[0].strip()
            commit = Commit(commit_id)
            date = cls.date(commit_lines)
            commit.date = str(date)
            commit.message = cls.message(commit_lines)

            commit.changes = cls.changes(commit_lines)
            author = cls.author(commit_lines)

            if author.email not in stats.authors:
                stats.authors[author.email] = author

            stats.authors[author.email].add_commit(commit)

        return stats