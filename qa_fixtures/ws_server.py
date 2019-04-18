import logging
import argparse
import json
import random
import signal
from uuid import uuid4
from tornado import (web, websocket, ioloop)

def keyboardInterruptHandler(signal, frame):
    logging.debug("KeyboardInterrupt (ID: {} {}) has been caught. Cleaning up...".
                  format(signal, frame))
    exit(0)

class ServerHandler(websocket.WebSocketHandler):
    clients = set()

    def __init__(self):
        super().__init__()

    def open(self):
        logging.debug('new connection')
        self.clients.add(self)
        message = self.generate_open_message()
        self.write_message(message)

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        logging.debug('new message')
        data = self.parse_message(message)
        logging.debug(str(data))

    def on_close(self):
        logging.debug('connection closed')
        if self in self.clients:
            self.clients.remove(self)

    @classmethod
    def heartbeat(cls, chan_id):
        hb = [chan_id, 'hb']
        msg = json.dumps(hb)
        for c in cls.clients:
            c.write_mesage(msg)

    def parse_message(self, message):
        try:
            data = json.loads(message)
        except ValueError:
            data = None
            logging.debug('message parsing error')
        return(data)

    def get_subscribe(self, data):
        subscription = {}
        if data.get('event') == 'subscribe':
            channel = data.get('channel')
            pair = data.get('pair')
            prec = data.get('prec')
            length = data.get('len')
        else:
            return subscription
        chan_id = random.randint(1,1000)
        subscription.update({'event': 'subscribed', 'channel': channel, 'chanId': chan_id, 'pair': pair})
        if channel == 'book':
            prec = 'P0' if prec is None else prec
            length = 25 if length is None else length
            freq = 'F0'
            subscription.update({'prec': prec, 'len': length, 'freq': freq})
        return subscription

    def generate_open_message(self):
        data = {}
        data.update({'event': 'info', 'version': 1.1,
                     'serverId': str(uuid4()),'platform':{'status':1}})
        message = json.dumps(data)
        return message

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