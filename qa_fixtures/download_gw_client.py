#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import requests
import argparse
import re
import os
from retrying import retry
from requests.exceptions import Timeout, ConnectionError

feed_url = 'http://ci2.ghcg.com/webstart/feed-client/feed-client.jar'
broker_url = 'http://ci2.ghcg.com/webstart/broker-client/broker-client.jar'
jmx_url = 'http://ci2.ghcg.com/webstart/management-client/management-client.jar'

@retry(stop_max_attempt_number=10)
def dowload_client(client_type:str, path='.'):
    if re.findall(r'feed|FEED|^f\w*|^F\w*', client_type):
        url = feed_url
    elif re.findall(r'broker|BROKER|^b\w*|^B\w*', client_type):
        url = broker_url
    elif re.findall(r'jmx|JMX|^j\w*|^J\w*|^man\w*', client_type):
        url = jmx_url

    fname = url.split('/')[-1]
    with open(os.path.join(path, fname), 'wb') as f:
        res = requests.get(url)
        f.write(res.content)
    return fname

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Download java console clients for testing')
    arg_parser.add_argument('client', type=str, help='client name to download',
                   choices=['broker', 'feed', 'jmx'])
    args = arg_parser.parse_args()

    print('file {} is dowloaded'.format(dowload_client(args.client)))


