#!/usr/bin/env python3

import re
import requests
from datetime import datetime,timezone

def get_symbols():
    sdb_snap = 'http://symboldb.prod.ghcg.com:8080/api/v2.0/snapshot'
    snap_params = {
        'id_regexp': '.*TOKENS.FX',
        'symbolTypes': 'FX_SPOT',
        'brokerProviders': 'TOKENSNET',
        'withSchedules': False
    }
    snap_headers = {'Accept': 'application/json'}
    res = requests.get(sdb_snap, params=snap_params, headers=snap_headers)
    return res.json().get('symbols')


def get_api_quotes(ticker):
    tokens_api = 'https://api.tokens.net/public/order-book/{}/'
    tokens_headers = {'Accept': 'application/json'}
    res = requests.get(tokens_api.format(ticker), headers=tokens_headers)
    return res.json()

def get_qring_quotes(exante_id):
    quote_api = 'http://qring.prod.ghcg.com/quote_api/v1/export/symbols/{}/quotes'
    quote_params = {'limit': 1}
    quote_headers = {'Accept': 'application/json'}
    res = requests.get(quote_api.format(re.sub('/', '%2f', exante_id)), params=quote_params, headers=quote_headers)
    return res.json()

if __name__ == '__main__':
    result = list()
    for sym in get_symbols():
        exante_id = sym.get('symbolId')
        ticker = re.sub('UST', 'USDT', exante_id).split('.')[0].lower().replace('/', '')
        item = dict()
        item.setdefault(exante_id, {'qring': None, 'book': None})
        item[exante_id]['qring'] = get_qring_quotes(exante_id)
        item[exante_id]['book'] = get_api_quotes(ticker)
        result.append(item)

    for i in result:
        print(i.keys())

    print('{:^20}|{:^120}|{:^120}'.format('ExanteId', 'qring', 'api'))
    print('{:^20}|{t:^39}|{b:^39}|{a:^40}|{t:^39}|{b:^39}|{a:^40}|'.format('', t='time', a='ask', b='bid'))
    for item in result:
        name = list(item.keys())[0]
        print('{:^20}|{t:^39}|{b:^39}|{a:^40}|'.format(name, t=item[name]['qring'][0]['time'],
                                                       b=str([item[name]['qring'][0]['bid']['pricedata'][0]['size'],
                                                          item[name]['qring'][0]['bid']['pricedata'][0]['price']]),
                                                       a=str([item[name]['qring'][0]['ask']['pricedata'][0]['size'],
                                                          item[name]['qring'][0]['ask']['pricedata'][0]['price']])),
                                                       end='')
        print('{t:^39}|{b:^39}|{a:^40}|'.format(t=datetime.
                                                fromtimestamp(int(item[name]['book']['timestamp']), timezone.utc).
                                                strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                                                b=str(item[name]['book']['bids'][0]),
                                                a=str(item[name]['book']['asks'][0])))


