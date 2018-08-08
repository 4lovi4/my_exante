#!/usr/bin/env python 
# -*- encoding: utf-8 -*-

import requests
import json
import logging
import argparse
from datetime import datetime
from dateutil import parser
import time

start_point = time.time()

url = 'http://orderdb.{}.ghcg.com/orders'
date_start = '2017-01-01T00:00:00Z'
date_end = '2017-10-03T00:00:00Z'
mSize = 1.5e6

parser = argparse.ArgumentParser(description='Getting all orders data from OrderDB')

parser.add_argument('--log-level', dest='loglevel', type=str, action='store', help='Specify log level', 
        choices=['debug', 'info', 'error', 'critical', 'warning'], default='debug'  )

parser.add_argument('-e', '--env', dest='env', type=str, action='store', default='prod',
        choices=['prod', 'demo', 'retail', 'test', 'stage', 'retail-demo'])

parser.add_argument('-s', '--max-size', dest='mSize', type=int, default=0)

args = parser.parse_args()

try:
    if args.mSize > 0:
        mSize = args.mSize
    else:
        pass
except:
    pass

print(args.loglevel.upper())

l = getattr(logging, args.loglevel.upper())

logging.basicConfig(level=l)

params = (('allAccounts', 'true'), ('automationOrders', 'false'),  ('maxSize', int(mSize)), 
        ('status', 'filled'), ('minDate', date_start), ('maxDate', date_end))

r = requests.get(url.format(args.env), params=params)

print(r.url, r.status_code)

with open('./temp.json', 'w') as f:
    json.dump(r.json(), f)

end_point = time.time()

execution = end_point - start_point

if execution > 60:
    print(round(execution, 0) // 60, ' m : ', round(execution, 0) % 60, ' s')
else:
    print(round(execution, 3), ' s')


