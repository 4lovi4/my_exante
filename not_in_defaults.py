#!/usr/bin/env python
#-*- coding: utf-8 -*-

#Parse all instruments that can be found to
#not with the default permissions to .csv file
#requested by Miks
#maybe should be improved

from libs import backoffice, symboldb
import re
import csv

bo = backoffice.BackOffice('prod')
so = symboldb.SymbolDB('prod')
al = so.get_them_all()
dl = bo.default_permissions_get()

fname = 'out.csv'
count = 0
ndl = list()


try:
    f = open(fname,'w')
    cf = csv.writer(f)
    header = ['ExanteId', 'Exchange', 'Type', 'Currency']
except:
    print('Can\'t open file {} for writing'.format(fname))


for s in al:
    b = 0
    try:
        comp = so.get_compiled(s['_id'])
    except:
        comp = None
    if comp:
        for x in dl:                                                                                                                           
            if re.search(x['symbolId'].replace('*', ''), comp['EXANTEId']): 
                b = 1
                break
            
    if (b != 1) and (comp != None):
        if len(ndl) == 0:
            cf.writerow(header)
        elif len(ndl) > 0:
            cf.writerow([comp['EXANTEId'],
                comp['exchange']['exchangeName'],
                comp['type'],
                comp['currency']])
        ndl.append(comp)
    else: 
        continue
    
f.close()

