#!/usr/bin/env python3

import requests
import yaml
import json
import logging
import sys

ORDERDB_URL = 'http://orderdb.test.ghcg.com/orders/{}'
HTTPGW_URL = 'http://internal-gateways.test.zorg.sh:8081/{}'

def create_session():
    session = requests.Session()
    return session

def post(session:requests.Session, url, headers=None, payload=None, *args, **kwargs):
    result = session.post(url = url, headers=headers, json=payload)
    return(result)

def get(session:requests.Session, url, headers=None, params=None, *args, **kwargs):
    result = session.get(url = url, headers=headers, json=payload)
    return(result)

def configi_parser(filename='./config.yaml'):
    with open(filename, 'r') as f:
        config = yaml.load(f)

