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

with open(fname,'w') as f:

    cw = csv.DictWriter(f,fieldnames=['Symbol', 'Description', 'Type', 'ISIN', 'Exchange'])
    cw.writeheader()
    opt_l = []
    fut_l = []
    stock_l = []
    fund_l = []
    cfd_l = []
    forex_l = []
    bond_l = []
    for item in asl:
        try:
            sc = so.get_compiled(item['_id'])
            if sc['isExpired'] == False and sc['isTrading'] == True:

                if sc['path'][1] == '052999553869f3d9f0e56ab9c646b90c' \
                        or sc['path'][1] == '051b63481ce4c0adbf6da09ef70c6ee1' \
                        or sc['path'][1] == 'i04e8b34bf97cb3be2a4d135041742e02' \
                        or sc['path'][2] == '3814be776dcc4d5cb30b47b9c7752a54' \
                        or sc['path'][1] == '054447a28c584d9e58d99769d797aa0c' \
                        or sc['path'][1] == '04d366a5838552f0223f2eda0822a806' \
                        or sc['path'][1] == '04f299363535b5bc9377eebc0223bfb9':
                            continue

                try:
                    s1 = sc['EXANTEId']
                    if re.match(r'.*[tT][eE][sS][tT].*', s1):
                        continue
                except:
                    continue
                try:
                    s2 = sc['shortName']
                except:
                    s2 = 'None'
                try:
                    s3 = sc['type']
                except:
                    continue
                try:
                    s4 = sc['identifiers']['ISIN']
                except:
                    s4 = 'None'
                try:
                    s5 = ex_name(sc['exchange']['name'])
                except:
                    s5 = 'None'
            else:
                continue
        except KeyError:
            continue

        ld = dict(Symbol='', Description='', Type='', ISIN='', Exchange='')
        if check_fut(s1) == True or check_opt(s1) == True:
            temps = s1.split('.')
            ld['Symbol'] = temps[0] + '.' + temps[1]
        else:
            ld['Symbol'] = s1
        ld.update(Description=s2, Type=s3, ISIN=s4, Exchange=s5)
        if s3 == 'STOCK':
            stock_l.append(ld)
        elif s3 == 'FUND':
            fund_l.append(ld)
        elif s3 == 'FUTURE':
            fut_l.append(ld)
        elif s3 == 'OPTION':
            opt_l.append(ld)
        elif s3 == 'FOREX':
            forex_l.append(ld)
        elif s3 == 'CFD':
            cfd_l.append(ld)
        elif s3 == 'BOND':
            bond_l.append(ld)
        else:
            continue

    print('stocks', len(stock_l))
    print('funds', len(fund_l))
    print('futures', len(fut_l))
    print('options', len(opt_l))
    print('forex', len(forex_l))
    print('cfd', len(cfd_l))
    
    result = list(itertools.chain(stock_l, fund_l, bond_l, del_dup(fut_l), del_dup(opt_l), forex_l, cfd_l))
    
    print('all:', len(result))

    for l in result:
        print(l)
        cw.writerow(l)

