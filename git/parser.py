from models import Commit
from models import Author
from models import Change
import datetime
import re
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
    Class has private helper method __get_file_change which counts file changes.
    """
    @classmethod
    def commit_id(cls, text: str):
        """
        Get commit ID "40 character hexadecimal number".
        
        Parameters
        ----------
        test : str
            Represents commit message string
        
        Returns
        -------
        str or None
            Commit ID
          """
        result = re.findall("[0-9a-f]{40}", text)
        if result == []:
            return None
        return result[0]

    @classmethod
    def author(cls, text):
        """
        Get author of the commit.
        
        Parameters
        ----------
        text : str
            Represents all data in a one commit message.
        
        Returns
        -------
        Author or None
            Commit author object
        """
        name = None
        email = None
        #print('-------')

        result = re.findall(r"Author:.*", text)
        if len(result) == 0:
            return None
        name = re.sub("(Author:.)|(.<.*>)", "", result[0])
        email = re.sub("(Author:.*<)|(>)", "", result[0])
        return Author(name=name, email=email)

    @classmethod
    def date(cls, text: str):
        """
        Get data of the commits.

        Parameters
        ----------
        text : list of str
            Represents all data in a one commit message.
        
        Returns
        -------
        datetime.datetime or None
            Commit date
        """
        line = re.findall("Date:.*", text)
        if len(line) == 0:
            return None
        date = datetime.datetime.strptime(line[0][6:].strip(),
                                          '%a %b %d %H:%M:%S %Y %z')
        return date

    @classmethod
    def message(cls, text: str):
        """
        Get commit message 
        
        Parameters
        ----------
        text : str
            Represents all data in a one commit message.
        
        Returns
        -------
        str
            Message string
        """
        return "".join(re.findall(r"\n*\s{4}.*", text))

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
    def changes(cls, text: str):
        """
        Get count of the line change in committed files
        
        Parameters
        ----------
        lines : str
            Represents all data in a one commit message.
        
        Returns
        -------
        list of Change
            Changes in commit
        """
        changes = []
        for line in re.finditer(r"\d*\t\d*\t.*", text):
            changes.append(cls.__get_file_change(line.group(0)))
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
                authors.append({
                    'name': parts[1],
                    'commit_cnt': int(parts[0].strip())
                })
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
            commit_id = cls.commit_id(commit_text)
            commit = Commit(commit_id)
            date = cls.date(commit_text)
            commit.date = str(date)
            commit.message = cls.message(commit_text)
            commit.changes = cls.changes(commit_text)
            author = cls.author(commit_text)

            if author.email not in stats.authors:
                stats.authors[author.email] = author

            stats.authors[author.email].add_commit(commit)

        return stats
