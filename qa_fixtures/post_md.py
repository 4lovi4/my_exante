#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import _json
import requests
import json
import argparse
import logging

gw_urls = {
        'test': 'http://internal-gateways.test.zorg.sh:8081/{end}',
        'stage': 'http://gateways2.stage.zorg.sh:8081/{end}',
        'prod': 'http://internal-gateways.prod.ghcg.com:8081/{end}',
        'cprod': 'http://cryptogw4.cprod.zorg.sh:8081/{end}'
    }

gw_head = {'Content-Type': 'application/json'}


def post_data(url, end, data):
    try:
        res = requests.post(url=url.format(end=end), json=data, headers=gw_head)
        logging.debug('posting: {} {} {}'.format(res.url, res.status_code, res.text))
        return res
    except Exception as err:
        logging.debug('Error occurred: {}'.format(err))
        return None

def post_quotes(env, quotes_data):
    return post_data(url=gw_urls.get(env), end='feed/quote', data=quotes_data)

def form_quote(symbol, bid_price=None, ask_price=None, bid_size=None, ask_size=None,
               timestamp=None, skip_validate=False):
    quote = {
        'symbol': symbol,
        'bid': {},
        'ask': {},
        'timestamp': timestamp,
        'skipValidation': skip_validate
    }

    quote['bid'] = {'levels': [{'price': bid_price, 'size': bid_size}]}
    quote['ask'] = {'levels': [{'price': ask_price, 'size': ask_size}]}

    if timestamp is None:
        del quote['timestamp']

    if bid_price is None:
        quote['bid'] = {}

    if ask_price is None:
        quote['ask'] = {}

    return quote


def post_trades():
    pass


def post_bond_data():
    pass


def post_option_data():
    pass


def post_aux_data():
    pass


def del_quote():
    pass


def post_error():
    pass

if __name__ == '__main__':
    aparser = argparse.ArgumentParser()
    aparser.add_argument('-e', '--env', choices=('test', 'stage', 'cprod', 'prod'),
                        default='test')
    aparser.add_argument('symbol', type=str)
    aparser.add_argument('mdtype', choices=('quote', 'trade', 'aux', 'bond', 'option'))
    aparser.add_argument('--bid-price', default=None)
    aparser.add_argument('--ask-price', default=None)
    aparser.add_argument('--ask-size', default=None)
    aparser.add_argument('--bid-size', default=None)
    aparser.add_argument('--trade')
    aparser.add_argument('--bond-data')
    aparser.add_argument('--option-data')
    aparser.add_argument('--aux-data')
    aparser.add_argument('--log-level', default='info', choices=('info', 'debug', 'error', 'warn'))
    args=aparser.parse_args()

    logging.basicConfig(level=args.log_level.upper())

    if args.mdtype == 'quote':
        quote = form_quote(args.symbol, bid_price=args.bid_price, bid_size=args.bid_size,
                           ask_price=args.ask_price, ask_size=args.ask_size)

        try:
            print(post_quotes(env=args.env, quotes_data=quote).status_code)
        except Exception as err:
            logging.debug(str(err))