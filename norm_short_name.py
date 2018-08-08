#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
import string
import sys

#parser = argparse.ArgumentParser()
#parser.add_argument('in_string', type=str, action='append', default='SHORT NAME')
#args = parser.parse_args()

in_string = sys.argv

print('old:', ''.join(in_string[_] + ' ' for _ in range(1, len(in_string))))

print('new:', ''.join(in_string[_][0].upper() + in_string[_][1:].lower() + ' ' for _ in range(1, len(in_string)))[:-1])

sys.exit(0)


