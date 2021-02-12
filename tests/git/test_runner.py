import sys
import pytest

sys.path.append('/')

from git import CmdRunner


def test_run():
    ''' Test on stdout without error'''
    if sys.platform == "win32":
        cmd = 'echo 5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03 > 5891b5b522_45.txt & cat 5891b5b522_45.txt'
    else:
        cmd = 'echo hello|sha256sum'
    cmd_out = CmdRunner.run(cmd, exit_on_fail=False)
    assert cmd_out.success
    assert '5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03' in cmd_out.stdout
    ''' Test on stderror'''
    cmd_out = CmdRunner.run('rm 5891b5b522_45.txt 2e846f6be03_67.txt', exit_on_fail=False)
    assert not cmd_out.success
