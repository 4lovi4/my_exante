#!/usr/bin/env python3
# -*- coding: utf8 -*-

import requests
import csv
import re
import tempfile
import json


def get_all_modules(monitor_url):
    try:
        r = requests.get(url=f"{monitor_url}modules")
    except requests.RequestException as err:
        print(err)
        return []
    return [{module.get("name"): module.get("properties")} for module in r.json()]


if __name__ == '__main__':
    csv_file = f"{tempfile.gettempdir()}/bc_list.csv"
    url = "http://monitor.prod.ghcg.com/"
    module_list = get_all_modules(monitor_url=url)

    with open(csv_file, 'w') as f:
        cw = csv.writer(f)
        cw.writerow(("module", "broker-client version"))
        for m in module_list:
            module_name = list(m.keys())[0]
            properties = list(m.values())
            if properties[0].get("javaLibraries"):
                for k, v in properties[0].get("javaLibraries").items():
                    if re.match(r"eu.exante.broker\:client", k):
                        cw.writerow((module_name, f"{k}:{v}"))
