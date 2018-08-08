#!/usr/bin/env python3
#-*- encoding: utf-8 -*-

import logging
import argparse
import getpass
from paramiko.client import SSHClient
from paramiko import ssh_exception
from paramiko.rsakey import RSAKey
from DNS import Request
import os
from dateutil.parser import parse
import re
from libs import monitor

def get_online_sessions(args):
    if args.env != 'prod':
        env = 'test'
    else:
        env = args.env
    mon = monitor.Monitor(env) 
    #all_fixb = mon.active_bridges()
    #fixb_names = [b['name'] for b in all_fixb]
    all_sessions = mon.fix_sessions()
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('sender_id', help='needed session SenderCompId', type=str, default='TEST', nargs='?')
    parser.add_argument('--env', help='environment, default is prod',
            choices=['prod', 'retail', 'test', 'demo'] , default='prod')
    parser.add_argument('-l', '--login', help='username for ssh. Default is system username', action='store',
            default=os.getenv('USER'))
    parser.add_argument('-o', '--online', help='get only online fix sessions', action='store_true')
    parser.add_argument('--log', help='log file. Default is None',
                    action='store', default=None)
    parser.add_argument('--log-format', help='log formating', action='store',
                    default='%(asctime)s : %(levelname)s : %(funcName)s : %(message)s')
    parser.add_argument('--log-level', help='log level. Default is warning',
                    action='store', default='warning',
                    choices=['debug', 'info', 'warning', 'error', 'critical'])

    args = parser.parse_args()

    loglevel = getattr(logging, args.log_level.upper())
    logging.basicConfig(filename=args.log, format=args.log_format, level=loglevel)

    if args.online:
        get_online_sessions(args)
