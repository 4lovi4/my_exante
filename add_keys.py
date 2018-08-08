#!/usr/bin/env python

#-*- coding: utf-8 -*-

import re
import os
import sys
import subprocess

command = ['/usr/bin/ssh-add']
pattern = '.*id_rsa$|.*buck.*key$|.*adya.ts$'

mykeys = [x.path for x in os.scandir(os.getenv('HOME') + '/.ssh')
        if re.match(pattern,x.path)]
for x in mykeys:
    command.append(x)

subprocess.run(command)

sys.exit(0)
