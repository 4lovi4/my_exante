#!/usr/bib/env python3
#-*- coding: utf-8 -*-

import requests

monitor_url = 'http://monitor.test.ghcg.com/{}'

class Monitor():
    def __init__(self, url=monitor_url):
        self.url = url
    
    def _get(self):
        pass

    def _post():
        pass

    def _put():
        pass

    def _delete():
        pass

    def get_modules():
        pass

class MockModule():
    def __init__(self, name='mock-test@module', url=monitor_url):
        self.name = name
        self.url = url
        self.monitor = Monitor(url=self.url)

    def update(self):
        pass

    def run(self):
        pass
    
    def delete(self):
        pass
