#!/usr/bin/env python
#-*-coding: utf-8 -*-

import requests
import datetime

tod = datetime.datetime.today().date()

url = 'http://bocore1.{}.ghcg.com/api/v2.0/overnights/{}'

env = 'retail'

params = {'accept': 'true', 'ignoreUndefinedRates': 'true'}

headers = {'Accept': 'application/json'}

r = requests.post(url.format(env, str(tod.isoformat())), headers=headers, params=params)

print(r.status_code()
