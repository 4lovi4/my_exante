#! /usr/bin/env python3

import threading
import requests
import json
from time import sleep
from datetime import datetime
import random

url = 'http://monitor.test.zorg.sh/{}'

modname = ('adya@bot', 'bot/adya')

states = ('OK', 'ERROR', 'WARN', 'INFO')

headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'charset': 'utf-8'}

modules_payload = {'indicators': [{'path': ['adya1'],
                                   'state': {'status': 'ERROR',
                                             'description': 'description 1',
                                             'statusName': '',
                                             'statusType': '',
                                             'timestamp': ''},
                                   'type': 'type1'},
                                  {'path': ['adya2'],
                                   'state': {'status': 'INFO',
                                             'description': 'description 2',
                                             'statusName': '',
                                             'statusType': '',
                                             'timestamp': ''},
                                   'type': 'type2'},
                                  {'path': ['adya3'],
                                   'state': {'status': 'WARN',
                                             'description': 'description 3',
                                             'statusName': '',
                                             'statusType': '',
                                             'timestamp': ''},
                                   'type': 'type3'},
                                  {'path': ['adya4'],
                                   'state': {'status': 'OK',
                                             'description': 'description 4',
                                             'statusName': 'status4',
                                             'statusType': 'status_type4',
                                             'timestamp': ''},
                                   'type': 'type3'}],
                   'properties': {'environment': 'test',
                                  'fullHostname': 'adya.bot',
                                  'project': 'QA',
                                  'team': 'qa'}
                   }


def create_mod(name: str, payload: dict):
    for _ in range(0, len(payload['indicators'])):
        payload['indicators'][_]['state']['timestamp'] = datetime.strftime(datetime.utcnow(), '%Y-%m-%dT%H:%M:%SZ')
    res = requests.put(url=url.format('modules/' + name), headers=headers, data=json.dumps(payload))
    return res


def update_mod(name: str, etag: str, payload=None):
    up_headers = headers
    up_headers.update({'If-Match': etag})
    res = requests.post(url=url.format('modules/' + name), headers=up_headers, json=payload)
    return res


if __name__ == '__main__':
    r = create_mod(random.choice(modname), modules_payload)
    print(r.status_code, r.text)
    etag = r.headers.get('ETag')
    for _ in range(15):
        payload = {'indicators': modules_payload['indicators'][0:1]}
        for i in payload['indicators']:
            i['state']['timestamp'] = datetime.strftime(datetime.utcnow(), '%Y-%m-%dT%H:%M:%SZ')
        if _ % 2 == 0:
            payload['indicators'][0]['state']['status'] = "ERROR"
        else:
            payload['indicators'][0]['state']['status'] = "ERROR"
        sleep(10)

        r = update_mod(random.choice(modname), etag, payload)
        etag = r.headers.get('ETag')
        if r.status_code == 409:
            r = create_mod(random.choice(modname), modules_payload)
            etag = r.headers.get('ETag')
            continue
        elif r.status_code == 200:
            continue
        else:
            print(r.status_code, r.text)
            break
