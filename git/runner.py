#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys

"""
Module provides command running and output handling functionality
"""


class CmdOutput:
    """
    CmdOutput(cmd_text, *output)
    
    Object for storing git command output
    
    Parameters
    ----------
    cmd_text : str
        Command string conatant
    
    *output : argv
        Command output parameters

    Attributes
    ---------
    cmd_text : str
        Command string conatant
    output : list of str
        Command output
    error : list of str
        Error output
    success_value : bool
        Command success state

    Properties
    ----------
    cmd : str
        Command string conatant
    stdout : list of str
        Command output
    stderror : list of str
        Error output
    success : bool
        Command success state
    """
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

    def __str__(self):
        return f"CmdOutput object - CMD: {self.cmd_text}"


class CmdRunner:
    """
    Functions for running and diplaying git command results
    
    Methods
    -------
    run(cmd, debug=False, exit_on_fail=True)
        Run git command in a subprocess and return a result
    verify(cmd_output: CmdOutput, debug: bool, exit_on_fail: bool)
        Display command output with formatted way and verify command 
        success status.
    """
    @classmethod
    def run(cls, cmd, debug=False, exit_on_fail=True):
        """
        Parameters
        ----------
        cmd : str 
            Command text  
        debug : bool, optional
        exit_on_fail : bool, optional
        
        Returns
        -------
        CmdOutput
        """
        if "^" in cmd and sys.platform == "win32":
            cmd = cmd.replace("^", "^^")
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True,
                             bufsize=16384,
                             encoding="utf-8",
                             errors="ignore",
                             shell=True)

        cmd_output = CmdOutput(cmd, p.communicate())
        cls.verify(cmd_output, debug, exit_on_fail)
        return cmd_output

    @classmethod
    def verify(cls, cmd_output: CmdOutput, debug: bool, exit_on_fail: bool):
        """
        Parameters
        ----------
        cmd_output : CmdOutput
        debug : bool, optional
        exit_on_fail : bool, optional
        
        Returns
        -------
        bool
            Successful verification
        """
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
