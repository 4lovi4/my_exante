#!/usr/bin/env python3

import argparse
import requests
from bs4 import BeautifulSoup
import re
import logging
import subprocess
import tempfile

app_url = 'http://updates-mobile.stage.exante.eu.s3-website.eu-central-1.amazonaws.com/'

def match_app(app, type, version):
    pass

def parse_doc(url=app_url):
    pass


if __name__ == '__main__':
    aparser = argparse.ArgumentParser()
    aparser.add_argument('-a', '--app', default='exante')
    aparser.add_argument('-t', '--type', choices=('release', 'stage'))
    aparser.add_argument('-v', '--version', default='last', help='pick the app version default value is the last')

    args = aparser.parse_args()
