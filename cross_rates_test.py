#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
import requests
import json
import sys
import os
import json

parser = argparse.ArgumentParser()
parser.add_argument('--c1', dest='c1', help='1st currency', type=str)
parser.add_argument('--c2', dest='c2', help='2nd currency', type=str)
parser.add_argument('-t', '--time-stamp', dest='t', metavar='TStamp', help='timestamp in ISO 8601 format', type=str)
parser.add_argument('-d', '--debug_cr', dest='debug_cr', help="Add debug crossrate path information", action='store_true')
parser.add_argument('--drop', dest='drop_cr', help="Drop cash", action='store_true')
parser.add_argument('-e', '--env', dest='env_cr', help="Specify environment", type=str, default='prod')
args = parser.parse_args()

#print('%s %s %s' % (args.c1, args.c2, args.t))

fname = os.getenv('HOME') + '/credentials.json'

with open(fname,'r') as f:
    data = json.load(f)


def drop_hist_quotes(env, data_creds):

    prod_url = 'http://backoffice.prod.ghcg.com/api/v2.0/quotecache/drop_historical_cache?allNodes=true'
    demo_url = 'http://backoffice.demo.ghcg.com/api/v2.0/quotecache/drop_historical_cache?allNodes=true'
    stage_url = 'http://backoffice.stage.ghcg.com/api/v2.0/quotecache/drop_historical_cache?allNodes=true'
    retail_url = 'http://backoffice.retail.ghcg.com/api/v2.0/quotecache/drop_historical_cache?allNodes=true'

    bo_sid = data_creds.get(env).get('backoffice')

    if env == 'prod':
        url = prod_url
        print('1')
    elif env == 'demo':
        url = demo_url
        print('2')
    elif env == 'stage':
        url = stage_url
        print('3')
    elif env == 'retail':
        url = retail_url

    print('env = {}'.format(env))
    print('url = {}'.format(url))
    headers = {'Content-Type': 'application/json',
             'X-Auth-SessionId': bo_sid}
    r = requests.post(url, headers=headers)
    print('{} - {} - {}'.format(str(r.url), str(r.status_code), str(r.text)))

    return

if args.drop_cr:
    drop_hist_quotes(args.env_cr, data)
    sys.exit(0)

stage_url = 'http://qring.stage.ghcg.com/crossrate_api/v1/crossrate'
prod_url = 'http://qring.prod.ghcg.com/crossrate_api/v1/crossrate'
demo_url = 'http://qring.demo.ghcg.com/crossrate_api/v1/crossrate'
retail_url = 'http://qring.retail.ghcg.com/crossrate_api/v1/crossrate'
rdata = {}

try:
    rdata.update({'from' : args.c1, 'to' : args.c2, 'timestamp' : args.t})
except AttributeError:
    rdata.update({'from' : args.c1, 'to' : args.c2})

if args.debug_cr:
    rdata.update({'debug' : 'true'})

print('rdata = {}'.format(rdata))
if args.env_cr == 'stage':
    r = requests.get(stage_url, params=rdata)
elif args.env_cr == 'prod':
    r = requests.get(prod_url, params=rdata)
elif args.env_cr == 'demo':
    r = requests.get(demo_url, params=rdata)
elif args.env_cr == 'retail':
    r = requests.get(retail_url, params=rdata)


print(r.url)
print('%s\n' % (str(r.status_code)))
print(r.text)
