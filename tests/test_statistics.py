import json
import hashlib
import sys

sys.path.append('./')

import loc
from _cmd import CmdOutput
from census import Statistics


class MockCmdRunner:
    @classmethod
    def run(cls, cmd, debug=False, exit_on_fail=True):
        """
        Imitates a regular CmdRunner.run function. According to passed argument
        opens the corresponding file, reads it and returns its contents that are
        previously recorded by running a command in real commandline.

        The files have unique names generated using md5sum of command
        string, hence, names of all files have 32 hex symbols length despite of
        the length of the command.

        Note: the function is supposed to be called by the class that is using
        :class:`CmdRunner`

        P.S. In order to add files containing the output of new commands, this
        simple reversed code can be pasted in :class:`CmdRunner.run` function
        before the return:

        ``import hashlib
        hash = hashlib.md5(cmd.encode())
        file_name = './desired_path/' + hash.hexdigest() + '.txt'
        with open(file_name, encoding="utf-8", mode="w",
                  errors='replace') as f:
            f.write(cmd_output.output)``

        Parameters
        ----------
        cmd - command
        debug - unused in mock class
        exit_on_fail - unused in mock class

        Returns - :class:`CmdOutput` as :class:`CmdRunner.run` function
        -------

        """
        _, _ = debug, exit_on_fail
        cmd2md5 = hashlib.md5(cmd.encode())
        file_path = 'tests/data/outputs/' + cmd2md5.hexdigest() + '.txt'
        with open(file_path, encoding="utf-8", mode="r", errors='replace') as f:
            ret = f.read()

        return CmdOutput(cmd, (ret, ''))


def test_statistics():
    with open('tests/data/expects/expect_stats.json') as f:
        expects = json.load(f)
    stats = Statistics('tests/data/samples', parse_step_len=3, runner=MockCmdRunner)
    assert stats.commits_count == expects['total_commits']
    assert stats.first_commit_date == expects["first_commit_date"]
    assert stats.last_commit_date == expects["last_commit_date"]
    stats.parse_authors()
    expected_authors = expects['parse_authors']['authors_by_email']
    for email in expected_authors:
        parsed = stats.authors.collection[email]
        reference = expected_authors[email]
        assert parsed.commits_count == reference['commits_count']
        assert parsed.lines_added == reference['lines_added']
        assert parsed.lines_deleted == reference['lines_deleted']

    loc.ignored_extensions_clear()
    loc.ignored_directories_clear()
    stats.count_lines()
    expected_languages = expects['count_lines']['languages']
    for language in expected_languages:
        parsed = stats.language_stats.collection[language]
        reference = expected_languages[language]
        assert parsed.code_lines == reference['code_lines']
        assert parsed.text_lines == reference['text_lines']
        assert parsed.comment_lines == reference['comment_lines']
        assert parsed.empty_lines == reference['empty_lines']
        assert parsed.files_count == reference['files_count']
