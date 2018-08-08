#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from libs.backoffice import BackOffice
from libs.mail_utils import send_mail
from threading import Timer, Lock, current_thread, Thread
from datetime import datetime, timedelta
from time import sleep
import argparse
import sys
import signal

macte_client_id = 'MXT7171'

class PeriodicMacteNotification:
    def __init__(self, interval, *args, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.bo = BackOffice('prod')
        self.client_id = macte_client_id
        self.interval = interval
        self.signals = (signal.SIGINT, signal.SIGTERM)
        self.is_running = False
        self.args = args
        self.kwargs = kwargs
        for s in self.signals:
            signal.signal(s, self._signal_handler)
        self.start()

    def _signal_handler(self, sig, frame):
        if sig in self.signals:
            print('Exiting the {}'.format(current_thread().name))
            self.stop()
            sys.exit(0)

    def start(self):
        print('Entering start()')
        self._lock.acquire()
        if not self.is_running:
            self.is_running = True
        self._lock.release()

    def stop(self):
        self._lock.acquire()
        self._timer.cancel()
        self.is_running = False
        self._lock.release()

    def macte_accs(self):
        accs = self.bo.client_accounts(self.client_id)
        return accs

    def get_margin(self):
        print('Entering get_margin()')
        margins = list()
        accs = self.macte_accs()
        for acc in accs:
            margin = dict()
            margin.setdefault('accountId', acc)
            margin['MU'] = float(self.bo.account_summary(acc['id']).\
                              get('metrics').get('marginUtilization'))
            margin['notify_status'] = False
            margins.append(margin)
        print(margins)

if __name__ == '__main__':
    aparser = argparse.ArgumentParser(description='Sheduled checking and '
                                      'notification macte about margin calls on their acounts')
    args = aparser.parse_args()
    macte_notifying = PeriodicMacteNotification(interval=10)
    sleep(100)
    macte_notifying.stop()
