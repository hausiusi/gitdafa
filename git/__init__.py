#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Docstring of the git package.

Package contains the runner.py module for running and properly displaying
git commands, the parser.py module for parsing various information from
results of git commands, and the control.py git control module for git command string constants.
"""

from .parser import Parse
from .runner import CmdOutput
from .runner import CmdRunner
from .control import Cmd
