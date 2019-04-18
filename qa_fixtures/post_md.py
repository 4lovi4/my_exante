#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import requests
import json
import argparse
import logging

gw_url = 'http://internal-gateways.{env}.zorg.sh:8081/{end}'
tickdb_url = 'http://tickdb3.{env}.zorg.sh/quote_api/v1/export/symbols/{sym}/{end}/'
gw_head = {'Content-Type': 'application/json'}


def post_quotes(symbol, data, env='test'):
    end = 'feed/quotes'
    try:
         res = requests.post(url = gw_url.format(env=env, end=end), json=data, headers=gw_head)
         print('posting:', res.url, res.status_code, res.text)
    except Exception as err:
         print('Error occured:', err)
         return None


def copy_prod_quotes(origin, copy=None, env='test'):
    end = 'quotes'
    if copy is None:
        post_to_sym = origin
    else:
        post_to_sym = copy
        origin_sym = origin
        tdb_params = {'limit': '1'}
        try:
            res = requests.get(url = tickdb_url.format(env='prod', sym=origin_sym, end='quotes'), params=tdb_params)
            tdb_quotes = res.json()[0]
        except Exception as err:
            print(res.url, 'Error occured:', err)
            return None
    data = dict()
    data.update({'symbol': post_to_sym,
                  'bid': {'yield': tdb_quotes['bid']['yield'], 
                          'levels': [{'price': tdb_quotes['bid']['pricedata'][0]['price'], 
                                      'size': tdb_quotes['bid']['pricedata'][0]['size']}]},
                  'ask': {'yield': tdb_quotes['ask']['yield'], 
                          'levels': [{'price': tdb_quotes['ask']['pricedata'][0]['price'], 
                                      'size': tdb_quotes['ask']['pricedata'][0]['size']}]}})
    post_quotes(post_to_sym, data=data,env=env) 
if __name__ == '__main__':
    logger = logging.Logger()
    aparser = argparse.ArgumentParser()
    #aparser.add_argument('command', choices=['post', 'copy'])
    #aparser.add_argument('symbols', nargs=argparse.REMAINDER)

    subparsers = aparser.add_subparsers()
    parse_copy = subparsers.add_parser('copy')
    parse_copy.add_argument('symbols', nargs='+')
    parse_copy = subparsers.add_parser('post')
    parse_copy.add_argument('symbol', nargs=1)

    args = aparser.parse_args()

    print('test', args) 
