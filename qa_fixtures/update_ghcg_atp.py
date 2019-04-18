#!/usr/bin/env python3
#-*-coding: utf-8-*-

import paramiko
import requests
import getpass
import socket

from check_apt import get_hosts
from check_apt import MONITOR_URL

env = 'load'

test_host = get_hosts(MONITOR_URL.format('test'), env)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
client.load_system_host_keys()

for host in test_host:
     try:
         client.connect(hostname=host, username=getpass.getuser(), timeout=3)
     except (paramiko.SSHException, TimeoutError, socket.timeout, socket.error) as err:
         print('Connection error')
         continue
     stdin, stdout, stderr= client.exec_command('lsb_release -r')
     ans = stdout.read().decode('utf-8')
     release = [a.rstrip('\n|\:') for a in ans.split('\t')][1]
     stdin, stdout, stderr= client.exec_command('dpkg-query --show ghcg-atp*')
     ghcg_atp = stdout.read().decode('utf-8')
     ghcg_atp_ver = ''
     if ghcg_atp:
         ghcg_atp_ver = [a.rstrip('\n') for a in ghcg_atp.split('\t')][1]
     print(host, release, ghcg_atp_ver)
     if release == '16.04' and ghcg_atp_ver:
         stdin, stdout, stderr= client.exec_command('sudo apt-get update')
         stdin, stdout, stderr= client.exec_command('sudo apt-get install ghcg-atp-deployment')
         ans = stdout.read().decode('utf-8')
     stdin, stdout, stderr= client.exec_command('dpkg-query --show ghcg-atp*')
     ghcg_atp = stdout.read().decode('utf-8')
     print(ghcg_atp)
     client.close()

