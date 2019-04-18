#!/usr/bin/env python3
#-*-coding: utf-8-*-

import requests
import argparse
import json
import re
import getpass

class Monitor():

    def __init__(self, env, user):
        self.url = 'http://monitor.{env}.ghcg.com/'.format(env=env)
        self.user = user

    def __get_mod(url, params=None):
        res = requests.get(url=url, params=params)
        if res.status_code == 200:
            try:
                return res.json()
            except json.JSONDecodeError:
                return None
        else:
            return None

    def __post_mod(url, params=None, data=None):
        headers = {'content-type': 'application/json',
                   'http-x-forwarded-user': self.user}
        res = requests.get(url=url,headers=headers, params=params, json=data)
        if res.status_code == 200:
            return res.text
        else:
            return None

    def get_incidents(self, state:str, anchor=None):
        state_values = ('all', 'open')
        if which not in state_values and anchor is not int:
            end_point = '{}{}'.format(self.url, 'incidents')
            incidents = self.__get_mod(end_point)
        elif which in state_values and anchor is not int:
            end_point = '{}{}/{}'.format(self.url, 'incidents', state)
            incidents = self.__get_mod(end_point)
        elif


        return incidents


    def drop_incidents(self, inc_id=None, mod_name=None, *args, **kwargs):
        if mod_name is None and inc_id is None:
            end_point = self.url.format('incidents')
            all_open = self.__get_mod('{}/open'.format(end_point))
            for incident in all_open:
                i = incident.get('id')
                self.__post_mod('{}/{}'end_point)
        end_point = '{}/{}'.format('incidents', inc_id) if inc_id is not None \
        else '{}/'.format('incidents')
        self.__post_mod()
        pass

    def get_module(self, mod_name=None):
        pass

    def create_mock_module(self, name='test-monitor@adya'):
        put_headers = headers
        payload = {'indicators': [], 'properties': {'team': 'techsupport'}}
        res = requests.put(monitor_url.format(name), headers=headers, data=json.dumps(payload))
        if res.status_code == 200:
            print(res.headers)
        else:
            print(res.status_code, res.text, res.headers)
            return None
        module = {'name': name, 'payload': payload, 'ETag': res.headers['ETag']}
        return module

    def post_updates(self, module):
        try:
            etag = module['ETag']
            payload = module['payload']
            name = module['name']
            while True:
                headers['If-Match'] = etag
                res = requests.post(monitor_url.format(name), headers=headers, data=json.dumps({}), timeout=1)
                if res.status_code == 200 and res.headers['ETag']:
                    etag = res.headers['ETag']
                else:
                    print(res.status_code, res.text)
                    break
                time.sleep(1)
        except KeyboardInterrupt as err:
            print(err, 'stop pulling shit')
            return 0

if __name__ == '__main__':

    aparser = argparse.ArgumentParser(description='script to handle the Exante monitor')
    aparser.add_argument('-e', '--env', help='specified environment for the monitor',
                         type=str, default='test', choices=('test', 'prod'))
    aparser.add_argument('-m', '--module', help='module name or regexp', default=None)
    aparser.add_argument('-u', '--user', help='username to post the monitor changes',
                         default=getpass.getuser())
    args = aparser.parse_args()

    monitor = Monitor(args.env, args.user)

    print(monitor.url)
