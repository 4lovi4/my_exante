#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import websockets
import asyncio
import ssl
import pathlib
import json
import argparse
import logging
import signal
import sys

binance_uri = 'wss://stream.binance.{}:9443/{}'
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# localhost_pem = pathlib.Path(__file__).with_name("localhost.pem")
# ssl_context.load_verify_locations(localhost_pem)


async def binance_stream(symbol, *args):
    uri_stream = ''
    if len(args) > 1:
        uri_stream = binance_uri.format('stream/?streams=')
        for stream in args:
            uri_stream += f'{symbol}@{stream}/'
        uri_stream = uri_stream[:-1]
    elif len(args) == 1:
        uri_stream = binance_uri.format('ws/')
        uri_stream += f'{symbol}@{args[0]}'
    async with websockets.connect(uri=uri_stream, ssl=True) as ws:
        data = await ws.recv()
        logging.debug(f'{type(data)} > {str(data)}')


def signal_handler(signum, frame):
    if signum == signal.SIGINT:
        sys.exit(1)


if __name__ == '__main__':
    aparser = argparse.ArgumentParser('WS-client')
    aparser.add_argument('-s', '--symbol', type=str, help='binance symbol name')
    aparser.add_argument('--streams', help='binance stream names', nargs='*')
    aparser.add_argument('--binance', choices=('je', 'com'), default='com',
                         help='binance exchange location')
    aparser.add_argument('--logging', choices=('error', 'debug', 'warning', 'critical', 'info'))
    args = aparser.parse_args()
    logging.basicConfig(level=args.logging.upper())
    signal.signal(signal.SIGINT, signal_handler)
    binance_uri = binance_uri.format()
    asyncio.get_event_loop().run_until_complete(binance_stream(args.symbol, 'ticker'))
