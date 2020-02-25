import logging
import argparse
import json
import random
import signal
import time
from datetime import datetime
from uuid import uuid4
from tornado import (web, websocket, ioloop)

"""
Currently hardcoded only for bitfinex subscription
"""

def keyboardInterruptHandler(signal, frame):
    logging.debug("KeyboardInterrupt (ID: {} {}) has been caught. Cleaning up...".
                  format(signal, frame))
    exit(0)

class ServerHandler(websocket.WebSocketHandler):
    clients = set()
    subscriptions = set()
    server_id = None
    version = '1.1'

    # def __init__(self):
    #     super().__init__(application, request)
    #     self.server_id = None

    def open(self):
        logging.debug('new connection')
        self.clients.add(self)
        message = self.generate_open_message()
        self.write_message(message)

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        logging.debug('new message: {}'.format(str(message)))
        data = self.parse_message(message)
        if data.get('event') == 'subscribe':
            subscription = self.Subscription(channel=data.get('channel'),
                                             pair=data.get('pair'))
            self.write_message(json.dumps(subscription.
                                          get_subscribe(data, malformed=True, del_field='channel')))
            self.write_message(json.dumps(subscription.gen_md()))
        logging.debug(str(data))

    def on_close(self):
        logging.debug('connection closed')
        if self in self.clients:
            self.clients.remove(self)

    def generate_open_message(self):
        data = {}
        server_id = str(uuid4())
        data.update({'event': 'info', 'version': 1.1,
                     'serverId': server_id,'platform':{'status':1}})
        message = json.dumps(data)
        return message

    def parse_message(self, message):
        try:
            data = json.loads(message)
        except ValueError:
            data = None
            logging.debug('message parsing error')
        return data


    class Subscription():

        ticker_data = ['channel_id',
                       150.01,         # bid
                       5,              # bid_size
                       160.1,          # ask
                       6,              # ask_size
                       2,              # daily_change
                       0.1,            # daily_change_perc
                       155.55,         #last_price
                       100,            #daily_volume
                       166.11123,      #high
                       151.3245]       #low

        trades_data = ['channel_id',
                       [10,            #trade_id
                        'timestamp',   #timestamp
                        150.05,        #price
                        -1]            #amount
                       ]

        book_data = ['channel_id',
                       [155.16781,      #price
                        12,             #count
                        2,              #amount - ask | + bid
                       ],
                       [155.8,
                       10,
                       0.5,
                       ]
                    ]

        def __init__(self, channel, pair):
            self.chan_id = random.randint(1,1000)
            self.channel = channel
            self.pair = pair

        def heartbeat(self):
            hb = [self.chan_id, 'hb']
            return hb

        def get_subscribe(self, data, malformed=False, del_field='channel'):
            subscription = {}
            if data.get('event') == 'subscribe':
                channel = data.get('channel')
                pair = data.get('pair')
                prec = data.get('prec')
                length = data.get('len')
            else:
                return subscription
            subscription.update({'event': 'subscribed', 'channel': channel,
                                 'chanId': self.chan_id, 'pair': pair})
            if channel == 'book':
                prec = 'P0' if prec is None else prec
                length = 25 if length is None else length
                freq = 'F0'
                subscription.update({'prec': prec, 'len': length, 'freq': freq})

            if malformed:
                subscription.pop(del_field)
            return subscription

        def gen_md(self):
            if self.channel == 'ticker':
                data = self.ticker_data

            elif self.channel == 'trades':
                data = self.trades_data
                data[1][1] = int(datetime.timestamp(datetime.utcnow()))

            elif self.channel == 'book':
                data = self.book_data

            data[0] = self.chan_id

            return(data)


if __name__ == '__main__':

    aparser = argparse.ArgumentParser(prog='ws mock server')
    aparser.add_argument('--log-level', default='debug',
                         choices=('info', 'warning', 'debug', 'error', 'critical'))
    aparser.add_argument('--log-file', default=None)
    aparser.add_argument('-a', '--address', default='')
    aparser.add_argument('-p', '--port', type=int, default=8511)
    args = aparser.parse_args()
    logging.basicConfig(level=args.log_level.upper(), filename=args.log_file)
    signal.signal(signal.SIGINT, keyboardInterruptHandler)
    logging.debug('Starting ws mock server...')
    app = web.Application([(r'/', ServerHandler)])
    app.listen(port=args.port, address=args.address)
    ioloop.IOLoop.instance().start()
