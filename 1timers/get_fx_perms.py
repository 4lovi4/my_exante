#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
import time
import csv
from libs import backoffice
from os import path, cpu_count
from tempfile import gettempdir
import multiprocessing
from retrying import retry

def conerror(exc):
    exception = [exceptions.ConnectionError, exceptions.Timeout, exceptions.ConnectTimeout, exceptions.ReadTimeout]
    print(exc, type(exc))
    return any([isinstance(exc, x) for x in exception])

def get_perms(acc_list:list):
    bo_url = 'http://backoffice.prod.ghcg.com/api/v2.0/accounts/{}/permissions/effective'
    header = {'Accept': 'application/json'}
    params = {'withExpired': 'false'}
    pattern = r'.*NY\.FX.*|.*NY2\.FX.*|.*E4\.FX.*|.*E5.FX.*|G.FX.*'
    fx_perms = []
    for acc in acc_list:
        perms = requests.get(bo_url.format(acc.get('id')), headers=header, params=params).json()
        for p in perms:
            try:
                if re.search(pattern, p.get('symbolId')) and (p.get('canView') or p.get('canTrade') or p.get('allowShort')):
                    print(multiprocessing.current_process().pid, ':', '[' + str(acc_list.index(acc)) +']', ':', acc, ':', p)
                    fx_perms.append([acc.get('id'), p.get('symbolId'), str(p.get('canView')), str(p.get('canTrade')), str(p.get('allowShort'))])
            except AttributeError as err:
                print(p, err)
                continue
    return(fx_perms)
@retry(wait_exponential_multiplier=5000, stop_max_attempt_number=10, retry_on_exception=conerror)
def div_list(in_list:list, div:int):
    out_list = []
    i = 0
    while i < len(in_list):
        b = i
        i += len(in_list) // div
        out_list.append(in_list[b:i])
    return out_list
bop = backoffice.BackOffice('prod')
all_accs = bop.accounts()
multi_accs = div_list(all_accs, cpu_count())
start = time.time()
fx_perms = []
pool = multiprocessing.Pool(processes=cpu_count())
multi_fx_perms = list(pool.map(get_perms, multi_accs))
fx_perms = sum(multi_fx_perms, [])
pool.close()
pool.join()
print('elapsed time:', time.time() - start)
fname = path.join(path.expanduser('~'), 'FX_permissions.csv')
header = ['account', 'symbolId', 'canView', 'canTrade', 'allowShort']
with open(fname, 'w') as f:
    cw = csv.writer(f)
    cw.writerow(header)
    for p in fx_perms:
        cw.writerow(p)
