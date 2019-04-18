#!/usr/bin/env python3

from libs import monitor

import re
import requests
from retrying import retry
import argparse


port_num = '8081'

get_hhtp_feed_hosts(env):
    hosts = list()
    return hosts

if __name__ == '__main__':
    aparser = argparse.ArgumentParser()
    aparser.add_argument('-e', '--env', type=str, default='prod',
                         choices=['prod', 'demo', 'cprod', 'retail',
                                  'test', 'cstage', 'load'])
    aparser.add_argument('-s', '--symbol', type=str, help='Instrument\'s ExanteId')

    args = aparser.parse_args()



