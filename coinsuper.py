#!/usr/bin/env python3

from time import time
from hashlib import md5
import argparse
import requests


coin_url = 'https://api.coinsuper.com/api/v1/{}'

symboldb_url = 'http://symboldb.{env}.ghcg.com/api/v2.0/{endpoint}'

def coin_common(key, sec):
    timestamp = int(time())
    params = dict(accesskey=key, secretkey=sec, timestamp=timestamp)
    sign = '&'.join(['{}={}'.format(k, params[k]) for k in sorted(params.keys())])
    md5_sign = md5(sign.encode('utf8')).hexdigest()

    data = dict(common={'accesskey':key, 'timestamp':timestamp, 'sign':md5_sign},
                data={})
    return data

def coin_post(data, endpoint, spec):
    data.setdefault(data=spec)
    res = requests(coin_url.format(endpoint), json=data)
    ans = res.json()


if __name__ == '__main__':

    aparser = argparse.ArgumentParser()
    aparser.add_argument('key', type=str, help='api access key')
    aparser.add_argument('sec', type=str, help='api secret key')

    args = aparser.parse_args()


