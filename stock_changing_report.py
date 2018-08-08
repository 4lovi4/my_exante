#! /usr/bin/env python3
# -*- coding: utf-8 -*-


from datetime import datetime, timezone
from dateutil import parser, relativedelta
from contextlib import suppress
from libs import symboldb
from libs.mail_utils import send_mail
import csv
import argparse
import logging
import tempfile
import os
import itertools
import re

sym_type = ['STOCK']
mail_to = ['techsupport@exante.eu']
mail_from = 'Robot <support@exante.eu>'


def get_stock_data(syms_list, sdb, time_term, *args):

    start_time = time_term[0]
    end_time = time_term[1]
    data_list = []
    for sym in syms_list:
        if (re.search(r'QUANT|SPREAD|STRANGLE', sym.get('symbolId'))):
            logging.debug(sym.get('symbolId')
                          + ' passed as non stock for really')
            continue

        doc = sdb.get(sym.get('symbol').get('_id'))
        # if current instrument not stock for really but index then skip it:
        if '05050a5894627e31fc6a5f73a93d3232' in \
                doc.get('content').get('path'):
            continue
        creation_time = parser.parse(doc.get('content').get('_creationTime'))
        if sym.get('symbol').get('expiryTime'):
            exp_time = parser.parse(sym.get('symbol').get('expiryTime'))
            logging.debug('{} expired {}'.format(sym.get('symbolId'),
                                                 exp_time.strftime('%Y-%m-%dT%H:%M:%S')))
        else:
            exp_time = datetime.min
            exp_time = exp_time.replace(tzinfo=timezone.utc)

        if (exp_time > start_time and exp_time < end_time
            and 'expired' in args) or \
                (creation_time > start_time and creation_time < end_time
                 and 'active' in args):
            try:
                if 'expired' in args:
                    data = {'symbol': sym.get('symbolId'),
                            'isin': sym.get('symbol').get('identifiers').get('ISIN'),
                            'date': exp_time}
                elif 'active' in args:
                    data = {'symbol': sym.get('symbolId'),
                            'isin': sym.get('symbol').get('identifiers').get('ISIN'),
                            'date': creation_time,
                            'leverageRate': sym.get('symbol').get('leverageRate'),
                            'extremeLeverageRate': sym.get('symbol').get('extremeLeverageRate'),
                            'extremeLeverageRateShort': sym.get('symbol').get('extremeLeverageRateShort'),
                            'leverageRateShort': sym.get('symbol').get('leverageRateShort')
                            }
                data_list.append(data)
            except AttributeError as err:
                logging.debug(str(err) +
                              sym.get('symbolId') + 'ISIN is None')
                #data_list.append((sym.get('symbolId', 'None')))

    return sorted(data_list, key=lambda k: k['date'])

def get_exp_stocks(sdb, time_term: tuple):

    status = 'expired'
    all_exp_syms = sdb.get_from_http(sym_type=sym_type,
                                     status=status, with_schedules=False)
    logging.debug(status + ': ' + str(len(all_exp_syms)))
    expired_list = get_stock_data(all_exp_syms, sdb, time_term, status)
    return expired_list


def get_new_stocks(sdb, time_term: tuple):
    status = 'active'
    all_active_syms = sdb.get_from_http(sym_type=sym_type,
                                        status=status, with_schedules=False)
    logging.debug(status + ': ' + str(len(all_active_syms)))
    new_list = get_stock_data(all_active_syms, sdb, time_term, status)
    return new_list

def get_new_leverage_stocks(sdb, time_term:tuple):
    sym_type = ['STOCK', 'CFD']
    status = 'active'
    all_active_syms = sdb.get_from_http(sym_type=sym_type,
                                        status=status, with_schedules=False)
    logging.debug(status + ': ' + str(len(all_active_syms)))
    new_list = get_stock_data(all_active_syms, sdb, time_term, status)
    result = list()
    for item in new_list:
        try:
            if item.get('leverageRate') < 1.0:
                result.append(item)
        except TypeError as err:
            logging.debug('{}: no leverage'.format(item['symbol']))
    return result

def create_csv(start_time, new_list, exp_list):
    header = ('symbolId', 'ISIN')
    csv_fname = 'stock_report_{}.csv'.format(start_time.strftime('%b%y'))
    csv_path = os.path.join(tempfile.gettempdir(), csv_fname)
    output_str = ''
    with open(csv_path, 'w') as f:
        cw = csv.writer(f)
        row = ('new added', ' ', 'disabled', ' ')
        cw.writerow(row)
        header *= 2
        cw.writerow(header)
        output_str += ' '.join(row) + '\n' + ' '.join(header) + '\n'
        for new, exp in \
                itertools.zip_longest(new_list, exp_list, fillvalue=' '):
            row = list()
            try:
                for l in (new, exp):
                    for k in ('symbol', 'isin'):
                        row.append(l[k])
            except TypeError as err:
                logging.debug('new: {} exp: {}'.format(str(new), str(exp)))
                row.extend('')
            cw.writerow(row)
            output_str += ' '.join(row) + '\n'
    return {'csv_path': csv_path, 'output': output_str}

def create_csv_leverage(start_time, stop_time, lev_list):
    header = ('SymbolId', 'ISIN', 'Leverage', 'Leverage short',
             'Extreme leverage', 'Extreme leverage short')
    csv_fname = 'stock_report_{}-{}.csv'.format(start_time.strftime('%d%b%y'),
                                                stop_time.strftime('%d%b%y'))
    csv_path = os.path.join(tempfile.gettempdir(), csv_fname)
    output_str = ''
    with open(csv_path, 'w') as f:
        cw = csv.writer(f)
        cw.writerow(header)
        output_str += ' '.join(header) + '\n'
        for item in lev_list:
            row = list()
            row.extend((str(item['symbol']), str(item['symbol']),
                        str(item['leverageRate']), str(item['leverageRateShort']),
                        str(item['extremeLeverageRate']), str(item['extremeLeverageRateShort'])))
            cw.writerow(row)
            output_str += ' '.join(row) + '\n'
    return {'csv_path': csv_path, 'output': output_str}

def parse_term(term):

    current_time = datetime.utcnow()
    if term == 'month':
        delta = relativedelta.relativedelta(months=1, year=current_time.year)
        start_date = current_time - delta
        start_date = start_date.replace(day=1, hour=0, minute=0,
                                        second=0, microsecond=0,
                                        tzinfo=timezone.utc)
        end_date = start_date
        end_date = end_date.replace(month=(start_date.month + 1))
    elif term == 'year':
        delta = relativedelta.relativedelta(years=1, year=current_time.year)
        start_date = current_time - delta
        start_date = start_date.replace(hour=0, minute=0, second=0,
                                        microsecond=0, tzinfo=timezone.utc)
        end_date = current_time
        end_date = end_date.replace(hour=0, minute=0, second=0,
                                    microsecond=0, tzinfo=timezone.utc)
    elif term == 'week':
        delta = relativedelta.relativedelta(days=7, year=current_time.year)
        start_date = current_time - delta
        start_date = start_date.replace(hour=0, minute=0, second=0,
                                        microsecond=0, tzinfo=timezone.utc)
        end_date = current_time
        end_date = end_date.replace(hour=0, minute=0, second=0,
                                    microsecond=0, tzinfo=timezone.utc)
    elif term == 'day':
        delta = relativedelta.relativedelta(days=1, year=current_time.year)
        start_date = current_time - delta
        start_date = start_date.replace(hour=0, minute=0, second=0,
                                        microsecond=0, tzinfo=timezone.utc)
        end_date = current_time
        end_date = end_date.replace(hour=0, minute=0, second=0,
                                    microsecond=0, tzinfo=timezone.utc)
    logging.debug('time period: [' + str(start_date) + ' - '
                  + str(end_date) + ']')
    return(start_date, end_date)


def send_mail_report(mail_to, mail_from, attach_path: str,
                     period: str, time_term: tuple, *args, **argsv):

    if argsv.get('leverage'):
        body = 'Here is the new added stocks and cfd report with leverage less then 1'
        ' during the last {}'.\
        format(period)
        subj = 'Stock changing report with leverage < 1 {}-{}.'\
            .format(time_term[0].strftime('%d%b%y'),
                    time_term[1].strftime('%d%b%y'))
    else:
        body = 'Here is the stock changing report during the last {}'.\
            format(period)
        subj = 'Stock changing report {}.'.format(time_term[0].strftime('%b%y'))

    logging.debug('Sending mail to {} with file {}'
                  .format(mail_to, attach_path))
    send_mail(mail_to, mail_from, subj, body, attachment=attach_path)

    return


if __name__ == '__main__':
    aparser = argparse.ArgumentParser()
    aparser.add_argument('-e', '--env', help='environment, default is prod',
                         choices=('prod', 'stage', 'test'), default='prod')
    aparser.add_argument('--dry-run', help='show data and do not execute',
                         action='store_true')
    aparser.add_argument('-t', '--term', type=str, default='month',
                         choices=['day', 'week', 'month', 'year'],
                         help='specify the last effective report term. \
                         Deault is the last month')
    aparser.add_argument('--email', help='send schedule to email',
                         nargs='+')
    aparser.add_argument('--leverage',
                         help='send report with the leverage value < 1',
                         action='store_true')
    aparser.add_argument('--log', help='log file. Default is None',
                         default=None)
    aparser.add_argument('--log-format', help='log formating',
                         default='%(asctime)s : %(levelname)s : \
%(funcName)s : %(message)s')
    aparser.add_argument('--log-level',
                         help='log level. Default is warning',
                         default='warning',
                         choices=['debug', 'info', 'warning',
                                  'error', 'critical'])

    args = aparser.parse_args()
    loglevel = getattr(logging, args.log_level.upper())
    logging.basicConfig(filename=args.log,
                        format=args.log_format, level=loglevel)
    sdb = symboldb.SymbolDB(args.env)
    time_term = parse_term(args.term)

    if args.email:
        mail_to = args.email

    if args.leverage:
        leverage_list = get_new_leverage_stocks(sdb, time_term)
        report = create_csv_leverage(time_term[0], time_term[1], leverage_list)
        if not args.dry_run:
            send_mail_report(mail_to, mail_from, report.get('csv_path'),
                              args.term, time_term, leverage=True)
            with suppress(FileNotFoundError):
                os.remove(report.get('csv_path'))
        else:
            logging.warning(report.get('output'))
    else:
        exp_stocks = get_exp_stocks(sdb, time_term)
        new_stocks = get_new_stocks(sdb, time_term)
        report = create_csv(time_term[0], new_stocks, exp_stocks)
        if not args.dry_run:
            send_mail_report(mail_to, mail_from, report.get('csv_path'),
                         args.term, time_term)
            with suppress(FileNotFoundError):
                os.remove(report.get('csv_path'))
        else:
            logging.warning(report.get('output'))
