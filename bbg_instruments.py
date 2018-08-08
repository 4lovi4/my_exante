#!/usr/bin/env python3
#*-* coding: utf-8 -*-

from libs import symboldb
import csv
import os
import argparse
import re
import itertools

so = symboldb.SymbolDB()
fname = os.getenv('HOME') + '/out.csv'

def check_opt(string):
    opt_re = r'^.*\..*\..*201.*\.[C,P].*'
    if re.match(opt_re, string):
        return True
    else:
        return False

def check_fut(string):
    fut_re = r'^.*\..*\..*201.?$'
    if re.match(fut_re, string):
        return True
    else:
        return False

def ex_name(string):
    exchange = string.split(' ')[0]
    exc_re = r'[\[,\],:]'
    return re.sub(exc_re, '', exchange)

def del_dup(dl):
    return list({r['Symbol']: r for r in dl}.values())

asl = so.get_them_all() 
bloom_acc = 'j4DH1Vm2-rrEX-d9MD-RxSp-8tWoNvdVqYdW'

with open(fname,'w') as f:

    cw = csv.DictWriter(f,fieldnames=['Symbol', 'Description', 'Type', 'Sedol'])
    cw.writeheader()
    opt_l = []
    fut_l = []
    stock_l = []
    fund_l = []
    cfd_l = []
    forex_l = []
    bond_l = []
    for item in asl:
        row = []
        try:
            sc = so.get_compiled(item['_id'])
                 if sc['isExpired'] == False and sc['isTrading'] == True:
                     for acc in sc['brokers']['accounts']:
                         if acc['accountId'] == bloom_acc:
                             if (acc['account']['enabled'] and sc['brokers']['accounts'].index(acc) == 0) or\
                                     (acc['account']['enabled'] and acc['account']['allowFallback']):
                                row.append(sc['EXANTEId'])
                                try:
                                    row.append(sc['shortName'])
                                except:
                                    row.append('None')
                                row.append(sc['type'])
                                try:
                                    row.append(sc['identifiers']['SEDOL'])
                                except:
                                    row.append('None')
                                print(row)
                                cw.writerow(row)
        except:
            continue
