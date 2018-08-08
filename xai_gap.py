#!/usr/bin/env python3.5
#-*- coding: utf-8 -*-

from libs import qring
from decimal import Decimal
from dateutil import parser

env = 'demo'

qr = qring.QRing(env)

symbol= 'XAI.EXANTE'

instruments = {
             'zec' : 'ZEC/USD.KRAKEN',
             'xrp' : 'XRP/USD.KRAKEN',
             'ltc' : 'LTC/USD.BITFINEX',
             'eth' : 'ETH/USD.BITFINEX',
             'etc' : 'ETC/USD.BITFINEX',
             'xmr' : 'XMR/USD.BITFINEX'
}

parameters = {
        'zec_multi': 0.02,
        'zec_base': 230.77,
        'xrp_multi': 0.34,
        'xrp_base': 0.181487,
        'xmr_multi': 0.08,
        'xmr_base': 93.64,
        'size': 1,
        'ltc_multi': 0.14,
        'ltc_base': 51.58,
        'eth_multi': 0.35,
        'eth_base': 292.33,
        'etc_multi': 0.07,
        'etc_base': 10.86,
        'base': 526640.85
        }                                                                   

def one_price_calc(p, multi, base):
    return (multi * (p - base) / base)

def common_price_calc(etc, eth, ltc, xmr, xrp, zec, parameters=parameters):
    price = Decimal(str(round(((one_price_calc(float(etc), float(parameters.get('etc_multi')), float(parameters.get('etc_base'))) +
        one_price_calc(float(eth), float(parameters.get('eth_multi')), float(parameters.get('eth_base'))) +
        one_price_calc(float(ltc), float(parameters.get('ltc_multi')), float(parameters.get('ltc_base'))) +
        one_price_calc(float(xmr), float(parameters.get('xmr_multi')), float(parameters.get('xmr_base'))) +
        one_price_calc(float(xrp), float(parameters.get('xrp_multi')), float(parameters.get('xrp_base'))) + 
        one_price_calc(float(zec), float(parameters.get('zec_multi')), float(parameters.get('zec_base')))) * 
        parameters.get('base') + parameters.get('base')) / 1000.0, 3)))
    return price

from_time = parser.parse('2017-09-26T21:25:00Z')
to_time = parser.parse('2017-09-27T10:51:00Z')

min_1 = {}                                                                                                                                  
min_5 = {}
hour_1 = {}
day_1 = {}

for i in instruments.keys():
    qclist = list(qr.get_qcandles(instruments.get(i), '1min', from_time, to_time, limit=5000))
    min_1[i] = qclist 

for i in instruments.keys():
    qclist = list(qr.get_qcandles(instruments.get(i), '5min', from_time, to_time, limit=5000))
    min_5[i] = qclist 

for i in instruments.keys():
    qclist = list(qr.get_qcandles(instruments.get(i), '1hour', from_time, to_time, limit=5000))
    hour_1[i] = qclist 

for i in instruments.keys():
    qclist = list(qr.get_qcandles(instruments.get(i), '1day', from_time, to_time, limit=5000))
    day_1[i] = qclist 

new_1min = []
new_5min = []
new_1hour = []
new_1day = []

n = 0
for (eth, ltc, zec, xmr, xrp, etc) in \
        zip(min_1.get('eth'), min_1.get('ltc'), min_1.get('zec'), min_1.get('xmr'), min_1.get('xrp'), min_1.get('etc')): 
            o_price = common_price_calc(etc.open_price, eth.open_price, ltc.open_price, xmr.open_price, xrp.open_price, zec.open_price)
            c_price = common_price_calc(etc.close_price, eth.close_price, ltc.close_price, xmr.close_price, xrp.close_price, zec.close_price)
            max_price = common_price_calc(etc.max_price, eth.max_price, ltc.max_price, xmr.max_price, xrp.max_price, zec.max_price)
            min_price = common_price_calc(etc.min_price, eth.min_price, ltc.min_price, xmr.min_price, xrp.open_price, zec.open_price)

            if min_price > c_price:
                min_price, c_price = c_price, min_price  
            if min_price > o_price:
                min_price, o_price = o_price, min_price
            if max_price < c_price:
                max_price, c_price = c_price, max_price  
            if max_price < o_price:
                max_price, o_price = o_price, max_price  

            xai_1min = qring.Candle('quotes', '1min', zec.timestamp, o_price, c_price, max_price, min_price)
            new_1min.append(xai_1min)

for (eth, ltc, zec, xmr, xrp, etc) in \
        zip(min_5.get('eth'), min_5.get('ltc'), min_5.get('zec'), min_5.get('xmr'), min_5.get('xrp'), min_5.get('etc')): 
            o_price = common_price_calc(etc.open_price, eth.open_price, ltc.open_price, xmr.open_price, xrp.open_price, zec.open_price)
            c_price = common_price_calc(etc.close_price, eth.close_price, ltc.close_price, xmr.close_price, xrp.close_price, zec.close_price)
            max_price = common_price_calc(etc.max_price, eth.max_price, ltc.max_price, xmr.max_price, xrp.max_price, zec.max_price)
            min_price = common_price_calc(etc.min_price, eth.min_price, ltc.min_price, xmr.min_price, xrp.open_price, zec.open_price)

            if min_price > c_price:
                min_price, c_price = c_price, min_price  
            if min_price > o_price:
                min_price, o_price = o_price, min_price
            if max_price < c_price:
                max_price, c_price = c_price, max_price  
            if max_price < o_price:
                max_price, o_price = o_price, max_price  

            xai_5min = qring.Candle('quotes', '5min', zec.timestamp, o_price, c_price, max_price, min_price)
            new_5min.append(xai_5min)

for (eth, ltc, zec, xmr, xrp, etc) in \
        zip(hour_1.get('eth'), hour_1.get('ltc'), hour_1.get('zec'), hour_1.get('xmr'), hour_1.get('xrp'), hour_1.get('etc')): 
            o_price = common_price_calc(etc.open_price, eth.open_price, ltc.open_price, xmr.open_price, xrp.open_price, zec.open_price)
            c_price = common_price_calc(etc.close_price, eth.close_price, ltc.close_price, xmr.close_price, xrp.close_price, zec.close_price)
            max_price = common_price_calc(etc.max_price, eth.max_price, ltc.max_price, xmr.max_price, xrp.max_price, zec.max_price)
            min_price = common_price_calc(etc.min_price, eth.min_price, ltc.min_price, xmr.min_price, xrp.open_price, zec.open_price)

            if min_price > c_price:
                min_price, c_price = c_price, min_price  
            if min_price > o_price:
                min_price, o_price = o_price, min_price
            if max_price < c_price:
                max_price, c_price = c_price, max_price  
            if max_price < o_price:
                max_price, o_price = o_price, max_price  

            xai_1hour = qring.Candle('quotes', '1hour', zec.timestamp, o_price, c_price, max_price, min_price)
            new_1hour.append(xai_1hour)

for (eth, ltc, zec, xmr, xrp, etc) in \
        zip(day_1.get('eth'), day_1.get('ltc'), day_1.get('zec'), day_1.get('xmr'), day_1.get('xrp'), day_1.get('etc')): 
            o_price = common_price_calc(etc.open_price, eth.open_price, ltc.open_price, xmr.open_price, xrp.open_price, zec.open_price)
            c_price = common_price_calc(etc.close_price, eth.close_price, ltc.close_price, xmr.close_price, xrp.close_price, zec.close_price)
            max_price = common_price_calc(etc.max_price, eth.max_price, ltc.max_price, xmr.max_price, xrp.max_price, zec.max_price)
            min_price = common_price_calc(etc.min_price, eth.min_price, ltc.min_price, xmr.min_price, xrp.open_price, zec.open_price)
            if min_price > c_price or min_price > o_price or max_price < c_price or max_price < o_price:
                continue
            xai_1day = qring.Candle('quotes', '1day', zec.timestamp, o_price, c_price, max_price, min_price)
            new_1day.append(xai_1day)

for qc in new_1hour:
    n += 1
    print(qc, '; n = {}'.format(n))
    

qr.post(symbol, new_1hour)
qr.post(symbol, new_1min)
qr.post(symbol, new_5min)
