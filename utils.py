#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import paramiko
import re
import os
import time

utils_url = 'utils3.prod.zorg.sh'

def restart_rej_mon(ssh_client, host, login, sudo):
    command = 'sudo supervisorctl restart rejects_monitor'
    ssh_client.connect(host, username=login, allow_agent=True)

    chan = ssh_client.get_transport().open_session()
    chan.get_pty()
    chan.setblocking(1)
    chan.exec_command(command)
    while chan.recv_ready()==False:
        out=chan.recv(4096)
        if re.search(b'password', out):
            chan.send(sudo + '\n')
        time.sleep(1)
    while chan.recv_ready():
        out += chan.recv(20000)
    #stdin, stdout, stderr = ssh_client.exec_command(command)
    #out = stdout.readlines()
    print(out)

if __name__ == '__main__':
    default_login = os.getenv('USER')
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--login', dest='login_name', default=default_login)
    parser.add_argument('-s', '--sudo', dest='sudo_pass', default='')
    args = parser.parse_args()

    print(args.login_name)
    
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    restart_rej_mon(client, utils_url, args.login_name, args.sudo_pass)
    client.close()
