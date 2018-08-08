#!/usr/bin/env python
#-*- coding: utf-8 -*-

import requests

if __name__ == '__main__':

    url = 'http://monitor.prod.ghcg.com/modules/gw-feed-nanex-stocks@ananas/indicators/subscriptions%7Cerror'

    r = requests.get(url)
    
    str1 = r.json()['state']['description']
    
    xpos = [i for i, c in enumerate(str1) if c == '×']
    
    print('```')
    for x in xpos:
        n = 0
        i = x
        while n < 1:
            print(str1[i].lstrip('× '), end='')
            i += 1
            if str1[i] == ':':
                n += 1
        print()
    print('```')

