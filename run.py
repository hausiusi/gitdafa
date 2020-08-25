#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmd_runner import CmdOutput, CmdRunner


if __name__ == "__main__":
    runner = CmdRunner()
    cmd = runner.run("git log", debug=True)
    print(f'Success: {cmd.success}')
    cmd = runner.run("git wrongarg", debug=True)
    print(f'Success: {cmd.success}')
