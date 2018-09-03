#!/usr/bin/env python3
#-*- coding: utf-8 -*-

"""
Tool to gentle restart ui-servers one by one at specified time
"""

import paramiko
import re
import pytz
import argparse
from datetime import datetime,timedelta,timezone

from libs import monitor

def remote_restart(user, host, sudo):
    pass


if __name__ == '__main__':
    aparser = argparse.ArgumentParser()
    aparser.add_argument('-e', '--env', type=str, default='prod',
                         choices=['prod', 'demo', 'cprod', 'retail',
                                  'test', 'cstage', 'load'])

    args = aparser.parse_args()
    if args.env in ['prod', 'demo', 'cprod', 'retail']:
        env = 'prod'
    elif args.env in ['test', 'stage', 'cstage', 'load']:
        env = 'test'
    mon = monitor.Monitor(env)
    ui_servers = [host['properties']['fullHostname'] \
                  for host in mon.active_uiservers() \
                  if re.search(r'.+\.{}\.\w+\.\w+'.format(args.env), host['properties']['fullHostname'])]
    print(ui_servers)


