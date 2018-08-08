#!/usr/bin/env python3.5
#-*- coding: utf-8 -*-

import requests
import json

p = {'allAccounts' : 'true', 'automationOrders': 'true', 'brokerUrl' : 'broker://lek.prod.ghcg.com', 
        'duration': 'day', 'status': 'active'}
url = 'http://orderdb.prod.ghcg.com/orders' 
r = requests.get(url, params=p)
print(r.status_code)


leks = r.json()

for x in leks['orders']:
    print(x['id'])



