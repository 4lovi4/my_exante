#!/usr/bin/env python3
#-*- coding: utf-8 -*- 

from libs import authdb
import argparse
import logging

def temp_token(auth:authdb.AuthDB, user, 
        token_name='temp', service='site', 
        token_value='dummy123'):
    if service not in ['site', 'atp']:
        return None
    token_posted = auth.token_post(user, token_name, token_value=token_value)
    tokenid = token_posted.get('tokenid')
    if tokenid is None:
        return tokenid
    res = auth.service(user, service, tokenid)
    if res.status_code != 204:
        return None
    else:
        return tokenid

def del_temp(auth:authdb.AuthDB, user, tokenid):
    user_info = auth.userinfo(user)
    for token in user_info.get('tokens'):
        if token.get('id') == tokenid and \
                token.get('name') != 'Main password':
                    res = auth.token_del(user, token)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', type=str, default='prod', choices=['prod', 'demo', 'test', 'stage'])
    parser.add_argument('-u', '--user', type=str)
    args = parser.parse_args()
    auth = authdb.AuthDB(args.env)
