import logging
import argparse
import json
import random
import signal
import time
from datetime import timedelta
from uuid import uuid4
from tornado import (web, websocket, ioloop)

def keyboardInterruptHandler(signal, frame):
    logging.debug("KeyboardInterrupt (ID: {} {}) has been caught. Cleaning up...".
                  format(signal, frame))
    exit(0)

class ServerHandler(websocket.WebSocketHandler):
    clients = set()
    subscriptions = set()

    def __init__(self):
        super().__init__()
        self.server_id = None

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
            self.write_message(subscription)
        logging.debug(str(data))

    def on_close(self):
        logging.debug('connection closed')
        if self in self.clients:
            self.clients.remove(self)

    def generate_open_message(self):
        data = {}
        self.server_id = str(uuid4())
        data.update({'event': 'info', 'version': 1.1,
                     'serverId': self.server_id,'platform':{'status':1}})
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
        def __init__(self, channel, pair):
            self.chan_id = random.randint(1,1000)
            self.channel = channel
            self.pair = pair

        def heartbeat(self):
            hb = [self.chan_id, 'hb']
            msg = json.dumps(hb)
            return msg

        def get_subscribe(self, data):
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
            return subscription

        def send_md(self):



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
