#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import sys
import argparse
import os

servers = [
        {'name' : 'atp1.demo.ghcg.com', 'feed' : 'feed-fix-bridge-uat-one', 'broker' : 'broker-fix-bridge-uat-one'},
        {'name' : 'atp2.demo.ghcg.com', 'feed' : 'feed-fix-bridge-uat-two', 'broker' : 'broker-fix-bridge-uat-two'},
        {'name' : 'ny-tmx-bridges1.prod.ghcg.com', 'feed' : 'feed-fix-bridge-ny', 'broker' : 'broker-fix-bridge-ny'},
        {'name' : 'eu-bridges2.prod.ghcg.com', 'feed' : 'feed-fix-bridge-eu', 'broker' : 'broker-fix-bridge-eu'},
        {'name' : 'irmo.ghcg.com', 'feed' : 'feed-fix-bridge-usa', 'broker' : 'broker-fix-bridge-usa'},
        {'name' : 'lon2-tmx.prod.ghcg.com', 'feed' : 'feed-fix-bridge-ln', 'broker' : 'broker-fix-bridge-ln'},
        {'name' : 'godric.ghcg.com', 'feed' : 'feed-fix-bridge-dsp', 'broker' : 'broker-fix-bridge-dsp'},
        {'name' : 'horus.ghcg.com', 'feed' : 'feed-fix-bridge-ld4', 'broker' : 'broker-fix-bridge-ld4'}
        ]

client = paramiko.SSHClient()
client.load_system_host_keys()


def_login = os.getenv('USER')

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--login', dest='login', type=str,
        help='Login to connect with ssh to the remote server. Default is the current username.')

args = parser.parse_args()

if args.login == None:
    login = def_login
else:
    login = args.login

client.connect(servers[0]['name'], username=login)
