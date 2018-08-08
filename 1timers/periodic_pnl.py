#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from libs.backoffice import BackOffice
from retrying import retry
import multiprocessing
import os
import itertools
import openpyxl
import requests
import time
import json

bo_url = 'http://backoffice.prod.ghcg.com/api/v2.0/{}'
draft_file = '/tmp/perf.json'

def list_chunk(it_list, size):
    it = iter(it_list)
    return iter(lambda: tuple(itertools.islice(it, size)), ())

@retry(stop_max_attempt_number=10)
def get_all_accs():
   params = {
       'fields': 'id',
       'legalEntity': 'Cyprus'
   }
   headers = {'Accept':'application/json'}
   res = requests.get(bo_url.format('accounts'), headers=headers, params=params)
   if res.status_code < 400:
       return res.json()
   else:
       return None

def calc_net_pnl(report:dict, header:list):
    output = []
    try:
        grossRealizedPnl = float(report.get('grossRealizedPnl'))
    except TypeError as err:
        grossRealizedPnl = 0.0
    try:
        commission = float(report.get('commission'))
    except TypeError as err:
        commission = 0.0
    try:
        couponPayments = float(report.get('couponPayments'))
    except TypeError as err:
        couponPayments = 0.0
    try:
        dividends = float(report.get('dividends'))
    except TypeError as err:
        dividends = 0.0
    try:
        excessMarginFee = float(report.get('excessMarginFee'))
    except TypeError as err:
        excessMarginFee = 0.0
    try:
        freeMoneyPremium = float(report.get('freeMoneyPremium'))
    except TypeError as err:
        freeMoneyPremium = 0.0
    try:
        interests = float(report.get('interests'))
    except TypeError as err:
        interests = 0.0
    try:
        other = float(report.get('other'))
    except TypeError as err:
        other = 0.0
    try:
        overnights = float(report.get('overnights'))
    except TypeError as err:
        overnights = 0.0
    try:
        portfolioValueChange = float(report.get('portfolioValueChange'))
    except TypeError as err:
        portfolioValueChange = 0.0
    try:
        rebates = float(report.get('rebates'))
    except TypeError as err:
        rebates = 0.0
    try:
        funded = float(report.get('funded'))
    except TypeError as err:
        funded = 0.0
    try:
        withdrawn = float(report.get('withdrawn'))
    except TypeError as err:
        withdrawn = 0.0
    try:
        totalConversionQuantity = float(report.get('totalConversionQuantity'))
    except TypeError as err:
        totalConversionQuantity = 0.0
    pnl = grossRealizedPnl + commission + couponPayments + dividends + excessMarginFee + freeMoneyPremium + \
        interests + other + overnights + portfolioValueChange + rebates + funded + \
        withdrawn + totalConversionQuantity
    others = report.get('otherTransactionTypes')
    out_others = ''
    for o in others:
        if others.index(o) + 1 < len(others):
            out_others += (o + ', ')
        elif others.index(o) + 1 == len(others):
            out_others += o
    output.append(report.get(header[0]))
    output.append(str(round(pnl, 2)))
    for h in header[2:]:
        if h == 'otherTransactionTypes':
            output.append(out_others)
            continue
        output.append(report.get(h))
    return output

@retry(stop_max_attempt_number=10)
def get_perf_report(accs, startDate='2018-04-01', endDate='2018-06-30'):
    headers = {'Accept': 'application/json'}
    perf_list = []
    for acc in accs:
        print(os.getpid(), ':', acc.get('id'))
        params = {
            'fromDate': startDate,
            'toDate': endDate,
            'currency': 'EUR',
            'accountId': acc.get('id')
        }
        res = requests.get(bo_url.format('reports/performance'), headers=headers, params=params)
        if res.status_code < 400:
            perf_report = res.json().get('statistics').get('total')
            perf_report['id'] = acc.get('id')
            perf_list.append(perf_report)
        else:
            print(res.status_code, res.text)
            continue
    return perf_list

if __name__ == '__main__':

    pool = multiprocessing.Pool(processes=os.cpu_count())
    start_time = time.time()
    all_accs = get_all_accs()
    acc_chunks = list(list_chunk(all_accs, len(all_accs) // os.cpu_count()))
    perf_reports = []
    multi_perf_reports = list(pool.map(get_perf_report, acc_chunks))
    perf_reports = sum(multi_perf_reports, [])
    pool.close()
    pool.join()
    perf_sorted = sorted(perf_reports, key=lambda p: p['id'])
    with open(draft_file, 'w') as f:
         json.dump(perf_sorted, f)
    header = list(perf_sorted[0].keys())
    output = []
    for report in perf_sorted:
        output.append(calc_net_pnl(report, header))
    print('elapsed time:', time.time() - start_time, 's')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'netRealizedPNL Apr-Jun 2018'
    ws.append(header)
    for out in output:
        ws.append(out)
    wb.save('netRealizedPNL_Apr-Jun_2018.xlsx')

