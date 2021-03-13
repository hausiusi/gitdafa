import datetime
import sys
import json
import os

sys.path.append("./")

from models import Author
from models import Change
from _cmd import CmdOutput

PARRENT_DIR = './tests/git/'

commit = {
    "ID":
    "15e9b586397a3e9e10a2ce6b7e0e40405efe6686",
    "Author":
    Author(name="Chuck Norris", email="gmail@chuck_norris.com"),
    "Date":
    datetime.datetime(year=2020,
                      month=8,
                      day=25,
                      hour=21,
                      minute=30,
                      second=54, tzinfo=datetime.timezone(datetime.timedelta(seconds=7200))),
    "changes": [
        Change(file_name='cmd_runner.py', added=53, deleted=13),
        Change(file_name='run.py', added=12, deleted=3)
    ],
    "message":
    '''Implement a basic runner for subprocess
    
    The patch provides class for running and verifying the command
    automatically. It returns standard output and standard error with
    success property to distinguish if the last command run failed when
    exit_on_fail is False.''',
    "str":
    '''15e9b586397a3e9e10a2ce6b7e0e40405efe6686
Author: Chuck Norris <gmail@chuck_norris.com>
Date:   Tue Aug 25 21:30:54 2020 +0200

    Implement a basic runner for subprocess
    
    The patch provides class for running and verifying the command
    automatically. It returns standard output and standard error with
    success property to distinguish if the last command run failed when
    exit_on_fail is False.
    
    Closes #2

53	13	cmd_runner.py
12	3	run.py
'''
}

cmd_test_data = '''
     4  SaturnR
     7  Zviad Mgaloblishvili
     127  Chuck Norris'''

test_cmd_out = CmdOutput('test_string', [cmd_test_data, ''])

# Prepare data for testing stats function
with open(PARRENT_DIR + 'stats.json', 'r') as f:
    js_stats = json.loads(f.read())
with open(PARRENT_DIR + 'test_commit.log', 'r') as f:
        test_commits = f.read()
stats_cmd_out = CmdOutput('test_string', [test_commits, '']) 

authors = {
    'test_data':   [{'name': 'SaturnR', 'commit_cnt': 4},
                    {'name': 'Zviad Mgaloblishvili', 'commit_cnt': 7},
                    {'name': 'Chuck Norris', 'commit_cnt':127}],
    'data': test_cmd_out
}
