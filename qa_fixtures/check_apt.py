#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import requests
import paramiko
import re
import argparse
import getpass
import socket
import logging
from retrying import retry
from itertools import zip_longest

HOST_URL = 'http://ngx1.dev.ghcg.com/nodes.txt'
MONITOR_URL = 'http://monitor.{}.ghcg.com/modules'

@retry(stop_max_attempt_number=10, wait_random_min=1000,
       wait_random_max=10000, retry_on_exception=requests.exceptions.RequestException)
def get_hosts_stat(url, env):
    hosts = list()
    res = requests.get(url)
    env_regexp = re.compile(r'.*\.{}\..*'.format(env))
    for line in res.text.split('\n'):
        if re.match(env_regexp, line):
            hosts.append(line)
    return(hosts)

@retry(stop_max_attempt_number=10, wait_random_min=1000,
       wait_random_max=10000, retry_on_exception=requests.exceptions.RequestException)
def get_hosts(url, env):
    modules = requests.get(url, headers={'accept': 'application/json'}).json()
    pattern = re.compile('.*\.{}\..*'.format(env))
    hosts = list()
    for module in modules:
        hostname = module.get('properties').get('fullHostname')
        if isinstance(hostname, str):
            if module.get('online') and hostname not in hosts and \
                re.match(pattern, hostname):
                    hosts.append(hostname)
    return(hosts)

def _init_ssh():
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    return client

def ssh_exec(host, user, package):

    keys = ('hostname', 'version', 'dist_ver', 'dist_name')
    commands = ('hostname',
                'dpkg-query --show {}'.format(package),
                'lsb_release -r',
                'lsb_release -c')
    client = _init_ssh()
    try:
        client.connect(hostname=host, username=user, timeout=5)
    except (paramiko.SSHException, TimeoutError,
            socket.timeout, socket.error) as err:
        logging.debug('can\'t connect to {} cause of {}'.
              format(host, str(err)))
        return False
    data = list()
    for command in commands:
        try:
            stdin, stdout, stderr= client.exec_command(command)
            output = stdout.read().decode('utf-8')
            try:
                data.append(output.split()[1])
            except IndexError as err:
                data.append(output)
        except paramiko.SSHException as err:
            logging.debug('can\'t execute the {} command  cause of {}'.
                  format(command, str(err)))
            client.close()
            return False
    if data[0]:
        info = dict()
        info.setdefault('apt', package)
        info.update(dict(zip_longest(keys, data[:len(keys)])))
        deb_dist = '\t'.join(data)
        logging.debug('{}'.format(deb_dist))
    client.close()
    return info


if __name__ == '__main__':

    aparser = argparse.ArgumentParser('remote apt checker')
    aparser.add_argument('-a', '--apt',
                         help='package name, default is ghcg-atp-deployment',
                         type=str, default='ghcg-atp-deployment')
    aparser.add_argument('-v', '--version', help='package version to check',
                         type=str, default='')
    aparser.add_argument('-d', '--dist', help='dist version, default is 16.04',
                         type=str, default='16.04')
    aparser.add_argument('-e', '--env', help='chosen environment', type=str,
                         default='demo')
    aparser.add_argument('-u', '--user', help='remote username', type=str,
                         default=getpass.getuser())
    aparser.add_argument('--log-format', help='log formating',
                         default='%(asctime)s : %(levelname)s : \
                     %(funcName)s : %(message)s')
    aparser.add_argument('--log-level', help='logging verbosity', type=str,
                         choices=('info', 'warning', 'debug', 'error'),
                         default='warning')
    args = aparser.parse_args()

    loglevel = getattr(logging, args.log_level.upper())
    logging.basicConfig(filename=None, format=args.log_format,
                        level=loglevel)

    package = args.apt
    ver = args.version
    dist = args.dist

    if args.env in ('prod', 'demo', 'cprod'):
        url = MONITOR_URL.format('prod')
    elif args.env in ('test', 'stage', 'cstage', 'load'):
        url = MONITOR_URL.format('test')

    hosts = get_hosts(url, args.env)

    result = list()
    result = [ssh_exec(host, args.user, package) for host in hosts]
    result = list(filter(lambda x: bool(x), result))

    if args.version:
        for res in result:
            if (res['version'] != args.version \
                and res['dist_ver'] == args.dist):
                print('\033[0;31;40m{} !\033[0m'.
                      format('\t'.join([x.lstrip('\n') for x in list(res.values())])))
            elif not res['dist_ver']:
                pass
            else:
                pass
    else:
        print ('Whole {} environment list:'.format(args.env))
        for res in result:
            print('\033[0;32;40m{}\033[0m'.
                  format('\t'.join(list(res.values()))))
            #if res['dist_ver']:
            #    pass
