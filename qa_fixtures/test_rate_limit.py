#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import requests
import json
import argparse
import re
import logging
import time
from threading import Thread, Event, Timer, current_thread
from queue import Queue
from retrying import retry
from requests.utils import quote as encode_url


class makeRequest:

    get_headers = {'Accept': 'application/json'}
    post_header = {'Content-Type': 'application/json'}

    def __init__(self, url, params=None, headers=None, payload=None):
        self.url = url
        self.params = params
        self.headers = headers
        self.payload = payload
        self.session = requests.Session()


    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def __request(self, method):
       req = requests.Request(method=method, url=self.url, params=self.params, 
                              headers=self.headers, json=self.payload)  
       prepreq = req.prepare()
       res = self.session.send(prepreq)
       try:
            ans = res.json()
       except json.decoder.JSONDecodeError:
            ans = None
       logging.debug('{} {} {}'.format(res.url, str(res.status_code), res.text))
       return ans       

    def get(self):
        return self.__request(method='GET')
        
    def post(self):
        return self.__request(method='POST')


class symbolDBApi:

    def __init__(self, sdb_url='http://symboldb.test.zorg.sh:9090'):
        self.sdb_url = ''.join([sdb_url, '/api/v1.0/{}'])
    
    def get_doc(self, instrument):
        params = {'symbolId_regexp': instrument}
        headers = makeRequest.get_headers 
        request = makeRequest(url=self.sdb_url.format('instruments'), 
                              params=params, headers=headers)
        doc = request.get()
        if len(doc) > 1:
            raise Exception('Responce is too large. Try to define the symbol regex.')
        return doc[0]

    def get_compiled(self, instrument):
        doc = self.get_doc(instrument)
        sdb_id = doc.get('_id')
        headers = makeRequest.get_headers
        requests = makeRequest(url=self.sdb_url.format('compiled_instruments/{}'.format(sdb_id)), 
                               headers=headers)
        compiled = requests.get()[0] 
        return compiled

    def get_mpi(self, instrument):
        compiled = self.get_compiled(instrument)
        return compile.get('orderMinPriceIncrement')

class tickDb3Api:

    def __init__(self, tdb3_url='http://tickdb3.test.zorg.sh'):
        self.tdb3_url = tdb3_url
        self.tdb3_export = '/quote_api/v1/export/symbols/'
        self.tdb3_history = '/quote_api/v1/history/{}'
        self.tdb3_price = '/price_api/v1/prices/{}'

    def get_last_tick(self, instrument):
        headers = makeRequest.get_headers
        params = {'limit': 1}
        url = ''.join((self.tdb3_url, self.tdb3_export, encode_url(instrument, safe=''), '/quotes'))
        request = makeRequest(url=url, headers=headers, params=params)
        last_tick = request.get()
        return last_tick

    def get_price(self, instrument):
        headers = makeRequest.get_headers
        params = {'symbolId': instrument}
        url = ''.join((self.tdb3_url, self.tdb3_price.format('snapshot')))
        request = makeRequest(url=url, headers=headers, params=params)
        price = request.get()
        return price

class httpBrokerApi:

    order_types = ('market', 'limit', 'stop',
                   'stop_limit', 'trailing_stop', 'twap', 'iceberg')

    order_durs = ('day', 'fill_or_kill', 'immediate_or_cancel',
                  'good_till_cancel', 'good_till_time', 'at_the_opening', 'at_the_close')

    def __init__(self, user, acc, api_url='http://internal-gateways3.test.zorg.sh:11005'):
        self.api_url = api_url
        self.api_orders = '/1.0/orders'
        self.scopes = {'X-Auth-Scopes': 'orders'}
        self.auth = {'X-Auth-User': user}
        self.account = acc

    def place_order(self, instrument, side, quantity, order_type='limit', duration='good_till_cancel', *args, **kwargs):
        if order_type not in self.order_types:
            raise ValueError('Wrong order type!')
        
        if duration not in self.order_durs:
            raise ValueError('Wrong order duration!')

        url = ''.join((self.api_url, self.api_orders))
        headers = makeRequest.post_header
        headers.update(self.auth)
        headers.update(self.scopes)
        payload = {
            'account': self.account,
            'instrument': instrument,
            'side': side,
            'quantity': quantity,
            'orderType': order_type,
            'duration': duration
        }
        if order_type == 'limit' and 'limitPrice' not in kwargs:
            raise ValueError('No price for the limit order')
            return None
        else:
            payload.update(kwargs)
        request = makeRequest(url, headers=headers, payload=payload)
        order_status = request.post()
        return order_status

    def get_order(self, order_id):
        url = ''.join((self.api_url, self.api_orders, '/', order_id))
        headers = makeRequest.get_headers
        headers.update(self.auth)
        headers.update(self.scopes)
        request = makeRequest(url, headers=headers)
        order_status = request.get()
        return order_status

    def __post_order(self, order_id, action, *args, **kwargs):
        if action not in ('cancel', 'replace'):
            raise ValueError('Wrong order modification!')
        url = ''.join((self.api_url, self.api_orders, '/', order_id))
        headers = makeRequest.post_header
        headers.update(self.auth)
        headers.update(self.scopes)
        payload = {
            'action': action,
            'parameters': {
            }
        }
        if action == 'replace':
            if 'quantity' not in kwargs.keys():
                raise ValueError('Quantity should be specified in replace')
                return None
            else:
                payload['parameters'].update(kwargs)
        request = makeRequest(url, headers=headers, payload=payload)
        order_status = request.post()
        return order_status
    
    def cancel_order(self, order_id):
        order_status = self.__post_order(order_id, 'cancel')
        return order_status

    def replace_order(self, order_id, quantity, limitPrice=None, stopPrice=None, placeDistance=None):
        order_status = self.__post_order(order_id, 'replace', quantity=quantity, 
                                         limitPrice=limitPrice, placeDistance=placeDistance)
        return order_status

class Placer(Timer):
    def __init__(self, order_queue:Queue, user, account, name='placer', *args, **kwargs):
        super().__init__(name=name)
        self.name = name
        self.queue = order_queue
        self.account = account
        self.user = user
        self.instrument = kwargs.get('instrument')
        self.side = kwargs.get('side')
        self.quantity = kwargs.get('quantity')
        self.limit_price = kwargs.get('limit_price')

    def run(self):
        logging.debug('{} {}'.format(current_thread().getName(), 'starting'))
        start = time.time()
        broker_api = httpBrokerApi(self.user, self.account)
        order = broker_api.place_order(self.instrument, self.side, self=quantity, limitPrice=self.limit_price)
        elapsed = time.time() - startself.instrument, self.side, self=quantity, limitPrice=self.limit_price)
        logging.debug('{} {}s {}'.format(current_thread().getName(), str(elapsed), 'elapsed'))


if __name__ == '__main__':
    aparser = argparse.ArgumentParser()
    aparser.add_argument('-o', '--ops', help='orders per time period')
    aparser.add_argument('-t', '--time', help='time period', default='1')
    aparser.add_argument('-u', '--user')
    aparser.add_argument('-a', '--account')
    aparser.add_argument('-i', '--instrument')
    aparser.add_argument('-s', '--side', choices=('buy', 'sell', 'b', 's'))
    aparser.add_argument('--log-level', 
                         choices=('warning', 'debug', 'error', 'info', 'critical'), 
                         default='info')
    args = aparser.parse_args()

    logging.basicConfig(level=args.log_level.upper()) 

    exante_id = 'ETH/BTC.BITIBU'
    username = 'adya@exante.eu'
    account = 'ADY8225.001'
    side = 'buy'
    quantity = '0.01'
    period = 1
    ops = 20

    sdb = symbolDBApi()

    order_mpi = sdb.get_compiled(exante_id).get('orderMinPriceIncrement')

    tdb = tickDb3Api()

    current_price = float(tdb.get_price(exante_id).get('price'))

    http_api = httpBrokerApi(username, account)

    interval = period / ops

    q = Queue(maxsize=10)

    placer = Placer(interval=interval, order_queue=q)

    placer.start()

    time.sleep(3)

    placer.join()

    #order = http_api.place_order(exante_id, side, quantity, limitPrice=str(current_price + order_mpi))
