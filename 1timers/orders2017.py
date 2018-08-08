#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from libs import symboldb
from dateutil import relativedelta
from dateutil import parser
import time
import multiprocessing
import datetime
import requests
import csv
import re

def url_time_str(timestamp:datetime.datetime):                                      
    return(timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))                                                            

def get_orders(start, stop, limit = 1000000):                         
    ret_dict = dict()              
    odb_url = 'http://orderdb.prod.ghcg.com/orders/'                                                       
    params = {                     
            'legalEntity': 'Malta',                                                                         
            'maxSize': str(limit),
            'minPlaceDate': url_time_str(start),
            'maxPlaceDate': url_time_str(stop),
            'status': 'terminated',  
            'automationOrders': 'true'                                         
            }                                                 
    header={'accept': 'application/json'}                           
    res = requests.get(odb_url, headers=header, params=params)
    print(multiprocessing.current_process().pid, ':', res.url)
    if res.json().get('foundMore'):
        print(res.json().get('foundMore'))                                                                      
        orders = get_orders(start, stop, limit + 100000)
    else:                                                                                        
        orders = res.json().get('orders')
    ret_dict[start.month] = (orders)                                                 
    return ret_dict        

if __name__ == '__main__':
    out_list = []
    pool = multiprocessing.Pool(processes=4)
    months = []
    start = parser.parse('2017-01-01T00:00:00Z')
    stop = start
    while stop < parser.parse('2018-01-01T00:00:00Z'):
        stop = start + relativedelta.relativedelta(months=1, year=2017)
        months.append((start, stop))
        start = stop
    out_list = list(pool.starmap(get_orders, months))
    pool.close()
    pool.join()

    all_orders = []
    for o in out_list:
        for key, val in o.items():
            all_orders.extend(val)

   start_time = time.time()                                            
   all_num = 0                                                                                                    
   report = dict()                                                                                                
   cash_types = {}                                                                  
   for o in all_orders:                                                                                           
        sym_type = None                                                                          
        order_type = None                                                                                          
        key = o.get('brokerUrl')                                                                                   
        if not (bool(re.match('.*automation.*|.*instant.*', key)) or \                           
            (len(o.get('orderState').get('fills'))) == 0):                                                         
            all_num += 1                                                                                       
            if cash_types.get(o.get('orderParameters').get('instrument')):                                     
                sym_type = cash_types.get(o.get('orderParameters').get('instrument'))                          
            else:                                                                                              
                if re.match('^.+\..+\.[A-Z]+\d{4}$', o.get('orderParameters').get('instrument')):                  
                    sym_type = 'FUTURE'                                             
                    print('derivative:', o.get('orderParameters').get('instrument'), sym_type)                                      
                elif re.match('^.+\..+\.\d*[A-Z]+\d{4}\.[P,C].*$', o.get('orderParameters').get('instrument')):    
                    sym_type = 'OPTION'                                                                            
                    print('derivative:',                                                                           
                    o.get('orderParameters').get('instrument'), sym_type)                                                           
                elif re.match('^.+\..+\/\d*[A-Z]+\d{4}\-\d*[A-Z]+\d{4}$', 
                            o.get('orderParameters').get('instrument')):                                                                
                    sym_type = 'CALENDAR_SPREAD'                                       
                    print('derivative:', o.get('orderParameters').get('instrument'), sym_type)
                else:                                                                                              
                    for i in all_instruments:
                        if i['symbolId'] == o.get('orderParameters').get('instrument'):
                            sym_type = i['symbol']['type']
                            print(all_num, ':', i['symbolId'], sym_type)
                            break
                        if not sym_type:      
                            try:
                                sym_type = so.get_historical_symbols(o.get('placeTime'), o.get('orderParameters').get('instrument'))['type']
                                print(all_num, ':', o.get('orderParameters').get('instrument'), sym_type)
                            except IndexError:
                                print(o.get('orderParameters').get('instrument'), 'no type!')
                                continue
                        cash_types[o.get('orderParameters').get('instrument')] = sym_type
                        order_type = o.get('orderParameters').get('type')
   try:
       report.setdefault(key, {'count': 0, 
           'BOND': {'count': 0, 'market': 0, 'limit': 0, 'stop': 0, 'stop_limit': 0}, 
           'STOCK': {'count': 0, 'market': 0, 'limit': 0, 'stop': 0, 'stop_limit': 0}, 
           'FUTURE': {'count': 0, 'market': 0, 'limit': 0, 'stop': 0, 'stop_limit': 0}, 
           'FX_SPOT': {'count': 0, 'market': 0, 'limit': 0, 'stop': 0, 'stop_limit': 0}, 
           'FOREX': {'count': 0, 'market': 0, 'limit': 0, 'stop': 0, 'stop_limit': 0}, 
           'OPTION': {'count': 0, 'market': 0, 'limit': 0, 'stop': 0, 'stop_limit': 0}, 
           'CALENDAR_SPREAD': {'count': 0, 'market': 0, 'limit': 0, 'stop': 0, 'stop_limit': 0}, 
           'CFD': {'count': 0, 'market': 0, 'limit': 0, 'stop': 0, 'stop_limit': 0}, 
           'FUND': {'count': 0, 'market': 0, 'limit': 0, 'stop': 0, 'stop_limit': 0}})
    report[key]['count'] += 1
    report[key][sym_type]['count'] += 1
    report[key][sym_type][order_type] += 1
    except (TypeError, KeyError) as err:
                 print('споткнулся на:', o.get('id'), 
                 o.get('orderParameters').get('instrument'), 
                 sym_type, order_type, err)
                 continue                     
     print(report)
     print('All:', all_num)
     print('process time:', round(time.time() - start_time, 1))
