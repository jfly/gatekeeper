#!/usr/bin/env python2

import sys
import subprocess
gittools = __import__('git-tools')
gittools.cdIntoScriptDir()

extraCmds = subprocess.list2cmdline(sys.argv[1:])
if extraCmds:
   extraCmds = ' ' + extraCmds

project = gittools.GitSensitiveProject(
     name='gatekeeper',
     compileCommand='npm install',
     runCommand='node gatekeeper.js' + extraCmds)
gittools.startGitSensitiveScreen('gatekeeper', [project])
