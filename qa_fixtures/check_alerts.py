#!/usr/bin/env python3
# -*- coding: utf8 -*-

import requests
import csv
import re
import tempfile
import json


alert_urls = {"prod": "http://price-alerts.prod.zorg.sh:80/",
              "cprod": "http://atp1.cprod.zorg.sh:8700/",
              "demo": "http://atp4.demo.zorg.sh:80/"}


def get_subs_by_user(env: str) -> dict:
    end = "api/v1/alerts"
    url = f"{alert_urls[env]}{end}"
    csv_file = f"{tempfile.gettempdir()}/{env}-alerts.csv"
    headers = {"Accept": "application/json"}
    result = {}
    try:
        r = requests.get(url=url, headers=headers)
        for pa in r.json():
            pa_symbols = set()
            for sq in pa.get("symbols"):
                pa_symbols.add(sq.get("symbolId"))
            user = pa.get("userId")
            if user not in result.keys():
                result.update({pa.get("userId"): pa_symbols})
            else:
                result[user] = result[user].union(pa_symbols)
    except requests.RequestException as err:
        print(err)
        return {}
    with open(csv_file, 'w') as f:
        cw = csv.writer(f)
        cw.writerow(("user", "symbols"))
        for k, v in result.items():
            cw.writerow((k, ', '.join(v)))
    return result


if __name__ == "__main__":
    for env in ('prod', 'cprod', 'demo'):
        get_subs_by_user(env)
