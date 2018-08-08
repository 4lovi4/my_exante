#!/usr/bin/env python3
#-*- coding: utf8 -*-

def ch_print():
    print("Проверка",end=' ')
    print("раз", "два", "три", sep="...")

import argparse
import os
import subprocess
from passlib.hash import bcrypt
import re
import string
import random



def edit_conf(acc_str, hash_str, conf_path, t):
    import json

def mail_output(acc_str, pass_str, hash_str, t):

    if (t == 'demo'):
        output = str('FIX TRADE' + '\n' +
                'address:port: fixuat2.exante.eu:8101' + '\n' +
                'sendercompid: {0}_TRADE_UAT'  + '\n' +
                'targetcompid: EXANTE_TRADE_UAT' + '\n' +
                'password: {1}' + '\n' +
                '\n' +
                'FIX FEED'  + '\n' +
                'address:port: fixuat2.exante.eu:8100' + '\n' +
                'sendercompid: {0}_FEED_UAT' + '\n' +
                'targetcompid: EXANTE_FEED_UAT' + '\n' +
                'password: {1}' + '\n' + 'hash: {2}').\
                        format(acc_str, pass_str, hash_str)
    elif (t == 'prod'):
        output = str('FIX TRADE' + '\n' +
                     'address:port: fixprod(ny|eu|dsp|usa|ld4).exante.eu:27001' +
                     ' (27101 for {{ln,ny}}-weekly)' +
                     '\n' + 'sendercompid: {0}_TRADE' + '\n' +
                     'targetcompid: EXANTE_TRADE' + '\n' +
                     'password: {1}' + '\n' +

                     'FIX FEED' + '\n' +
                     'address:port: fixprod(ny|eu|dsp|usa|ld4).exante.eu:27000' +
                     ' (27100 for {{ln,ny}}-weekly)' +
                     '\n' + 'sendercompid: {0}_FEED' + '\n' +
                     'targetcompid: EXANTE_FEED' + '\n' +
                     'password: {1}' + '\n' + 'hash: {2}').format(acc_str, pass_str, hash_str)
    print('\n' + output + '\n')
    return()


def gen_pass(length=19):
    pass_str = ''.join(random.SystemRandom().choice(re.sub('[\'\"`_\x0b\x0c\t\n\r ]', '', string.printable)) for _ in range(length))
    return pass_str


#   pass_str = subprocess.check_output("pwgen -syN1 18", shell=True).\
#        decode("utf-8").rstrip('\n')
if __name__ == '__main__':
    pass_str = "i)03R!zqJJYh"
    parser = argparse.ArgumentParser()
    parser.add_argument('account', default='XYZ123',
                        help='name of customer\'s account', type=str)
    parser.add_argument('--atype', metavar='<TYPE>', default='demo',
                        help='environment type', action='store', type=str)
    parser.add_argument('--pasw', default=None, type=str,
                        help='password')
    args = parser.parse_args()
    random.seed()
    if args.pasw:
        pass_str = args.pasw
    else:
        pass_str = gen_pass()
    hash_str = bcrypt.using(ident='2a').encrypt(pass_str)
    t = args.atype
#   print(t + ' - ' + str(type(args.atype)))
    mail_output(args.account, pass_str, hash_str, t)
