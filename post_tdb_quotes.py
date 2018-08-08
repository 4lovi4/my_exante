#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import monitor
import requests
import paramiko
from dateutil import parser
from datetime import datetime
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool to push random quotes to tdb. Sometimes is needed to adjust AS or 
            any other historical data from tdb')
    parser.add_argument('symbol', '-s', help='instrument\'s ExanteId to push the quotes', type=str, default='TEST.TEST', nargs='?')
    parser.add_argument('quote', '-q', help='string <\"bid, ask, size, datetime ISO8601\"> contains quote data to push in tdb',
            type=str, default='1, 1, 1, 2018-01-01T00:00:00Z', nargs='?')
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
    parser.add_argument('--dry-run', action='store_true')

    args = parser.parse_args()

    loglevel = getattr(logging, args.log_level.upper())
    logging.basicConfig(filename=args.log, format=args.log_format, level=loglevel)

    pass

