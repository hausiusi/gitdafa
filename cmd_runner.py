#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys


class CmdOutput:
    def __init__(self, cmd_text, *output):
        self.cmd_text = cmd_text
        self.output = str(output[0][0]).strip('\n')
        self.error = str(output[0][1]).strip('\n')
        self.success_value = self.error == ''

    @property
    def cmd(self):
        return self.cmd_text

    @property
    def stdout(self):
        return self.output

    @property
    def stderror(self):
        return self.error

    @property
    def success(self):
        return self.success_value


class CmdRunner():
    def run(self, cmd, debug=False, exit_on_fail=True):
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True,
                             shell=True)
        cmd_output = CmdOutput(cmd, p.communicate())
        self.verify(cmd_output, debug, exit_on_fail)
        return cmd_output

    def verify(self, cmd_output: CmdOutput, debug: bool, exit_on_fail: bool):
        if debug:
            print(f"Executed: '{cmd_output.cmd}'")
            print(f"Standard output: '{cmd_output.stdout}'")
            print(f"Standard error: '{cmd_output.stderror}'")
        if not cmd_output.success:
            print(
                f"Failed to execute: '{cmd_output.cmd}' with error: '{cmd_output.error}'"
            )
            if exit_on_fail:
                print("Exiting the program")
                sys.exit(-1)
            return False
        else:
            return True
