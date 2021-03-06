#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import subprocess
import json
import time
import argparse
import uuid
import logging
import os
import sys
import threading
import re
import paramiko
import DNS

from urllib.parse import urlparse

TIMEOUT = 5
CON_TIMEOUT = 0.5
DISC_TIMEOUT = 0.9
PLACE_TIMEOUT = 0.3

blocking_hosts = ('api.hitbtc.com', 'www.bitmex.com', 'api.bitfinex.com',
                  'api.globitex.com', 'api.coinsuper.com', 'api.binance.com',
                  'stream.binance.com', 'cex.io', 'bittrex.com', 'kuna.io',
                  'real.okcoin.com')

def broker_proc(brc_path):
    if os.path.exists(brc_path):
        com = 'java -jar {} --ui json'.format(brc_path)
        proc = subprocess.Popen(com.split(), bufsize=1, universal_newlines=False,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

    else:
        sys.exit('Wrong filename for broker client')

    return proc

def __put(stdin, payload:dict):
    logging.debug('sending {}'.format(str(payload)))
    #print('sending {}'.format(str(payload)))
    stdin.write('{}\n'.format(json.dumps(payload)).encode('utf-8'))
    stdin.flush()

def read_out(proc:subprocess.Popen):
    logging.debug('getting the response:')
    resp = None
    for line in iter(proc.stdout.readline, b''):
        resp = json.loads(line.decode('utf-8'))
        logging.debug(str(resp))
        #print(str(resp))
        if resp.get('state') == 'closed' \
                and resp.get('event') == 'connection_state':
            break
    return resp

def terminate_proc(proc:subprocess.Popen):
    proc.stdin.close()
    proc.stderr.close()
    proc.stdout.close()
    proc.terminate()
    proc.wait(timeout=0.1)

def connect(proc:subprocess.Popen, brokerUrl):
    con_id = str(uuid.uuid4())
    payload = {'command': 'connect',
               'connection': con_id,
               'url': brokerUrl
               }
    __put(proc.stdin, payload)
    return(con_id)

def disconnect(proc:subprocess.Popen, con_id):
    payload = {'command': 'disconnect',
               'connection': con_id,
               }
    __put(proc.stdin, payload)

def place(proc:subprocess.Popen, con_id, username, acc,
          instrument, side, qty, order_type, duration,
          brokerAccount_name=None, brokerAccount_clientid=None,**kwargs):
    order_id = str(uuid.uuid4())
    payload = {
        'command': 'place',
        'connection': con_id,
        'id': order_id,
        'username': username,
        'exanteAccount': acc,
        'brokerAccount': {
            'name': brokerAccount_name,
            'clientId': brokerAccount_clientid
        },
        'orderParameters': {
            'instrument': instrument,
            'side': side,
            'quantity': qty,
            'type': order_type,
            'duration': duration
        }
    }
    payload['orderParameters'].update(kwargs)
    __put(proc.stdin, payload)

    return(order_id)

def place_market(proc:subprocess.Popen, con_id, username, acc,
                 instrument, side, qty, duration,
                 brokerAccount_name=None, brokerAccount_clientid=None):
    return place(proc, con_id=con_id, username=username, acc=acc,
                 instrument=instrument, side=side,
                 qty=float(qty), order_type='market',
                 duration=duration,
                 brokerAccount_name=brokerAccount_name,
                 brokerAccount_clientid=brokerAccount_clientid)

def place_limit(proc:subprocess.Popen, con_id, username, acc,
                instrument, side, qty, duration, limit_price,
                brokerAccount_name=None, brokerAccount_clientid=None):
    return place(proc, con_id=con_id, username=username, acc=acc,
                 instrument=instrument, side=side,
                 qty=float(qty), order_type='limit',
                 duration=duration, brokerAccount_name=brokerAccount_name,
                 brokerAccount_clientid=brokerAccount_clientid,
                 limitPrice=float(limit_price))

def cancel (proc:subprocess.Popen, con_id, order_id, username):
    new_mod_id = str(uuid.uuid4())
    payload = {
                'command': 'cancel',
                'connection': con_id,
                'id': order_id,
                'username': username,
                'currentModificationId': order_id,
                'newModificationId': new_mod_id
    }
    __put(proc.stdin, payload)

def connect_gw(gw_url):
    if re.search(r'^feed', gw_url):
        gw_srv = re.sub(r'feed\://', '_feed._tcp.', gw_url)
        srv = True
    elif re.search(r'^broker', gw_url):
        gw_srv = re.sub(r'broker\://', '_broker2._tcp.', gw_url)
        srv = True
    elif re.search(r'^.*\..*\.zorg|ghcg.sh|com$', gw_url):
        gw_host = gw_url
        srv = False
    else:
        return None
    if srv:
        DNS.ParseResolvConf()
        srv_req = DNS.Request(qtype='srv')
        srv_resp = srv_req.req(gw_srv)
        gw_host = srv_resp.answers[0]['data'][-1]
        logging.debug('gw hostname: {}'.format(gw_host))

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.load_system_host_keys()
    ssh_client.connect(gw_host, username=os.getenv('USER'))

    return(ssh_client)

def resolve_hosts(host_list, gw_url):
    url_base = urlparse(gw_url).netloc.split('.')[0]
    DNS.ParseResolvConf()
    dns_request = DNS.Request()
    ip_list = list()
    if url_base == 'metacrypto':
        url_base = 'bitfinex'
    regex = re.compile(url_base)
    filtered_host = filter(regex.search, host_list)
    for hostname in filtered_host:
        dns_resp = dns_request.req(hostname)
        item = {hostname: list()}
        for ans in dns_resp.answers:
            if re.match(r'\d+\.\d+\.\d+\.\d+', ans.get('data')):
                item[hostname].append(ans.get('data'))
        ip_list.append(item)
    return(ip_list)

def send_comand(ssh_client, com):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(com)
        out = stdout.read().decode('utf-8')
        logging.debug(out)
    except paramiko.SSHException as err:
        logging.debug('error while executing the command {}'.format(str(err)))

def kill_con(ssh_client:paramiko.SSHClient, host_list):
    for host in host_list:
        for domen, ips in host.items():
            comand = 'tcpkill -9 host {0} > /dev/null 2>&1 &'.\
                format(domen)
            send_comand(ssh_client, comand)

def unkill_con(ssh_client:paramiko.SSHClient, host_list):
    for host in host_list:
        for domen, ips in host.items():
            for ip in ips:
                comand = 'sudo killall tcpkill'
                send_comand(ssh_client, comand)

def drop_con(ssh_client:paramiko.SSHClient, host_list):
    for host in host_list:
        for domen, ips in host.items():
            comand = 'sudo iptables -I INPUT -s {0} -j DROP && sudo iptables -I OUTPUT -d {0} -j DROP'.\
                format(domen)
            send_comand(ssh_client, comand)

def enable_con(ssh_client:paramiko.SSHClient, host_list):
    for host in host_list:
        for domen, ips in host.items():
            for ip in ips:
                comand = 'sudo iptables -D INPUT 1 && sudo iptables -D OUTPUT 1'
                send_comand(ssh_client, comand)

def disc_gw(ssh_client:paramiko.SSHClient):
    ssh_client.close()

if __name__ == '__main__':
    aparser = argparse.ArgumentParser()
    aparser.add_argument('--log-level', default='info',
                         choices=['debug', 'info', 'error', 'warning'])
    aparser.add_argument('--log-format', help='log formating',
                         default='%(asctime)s : %(levelname)s : \
                         %(funcName)s : %(message)s')
    aparser.add_argument('--path', type=str, help='broker-client full pathname',
                         default='./broker-client.jar')
    aparser.add_argument('--gw-url', type=str)

    aparser.add_argument('-u', '--user', type=str)
    aparser.add_argument('-a', '--acc', type=str)
    aparser.add_argument('-i', '--instrument', type=str)
    aparser.add_argument('-s', '--side', type=str,
                         choices=['buy', 'sell'])
    aparser.add_argument('-t', '--type', type=str, choices=['market', 'limit',
                                                            'stop', 'stop_limit',
                                                            'twap', 'iceberg',
                                                            'trailing_stop'])
    aparser.add_argument('-d', '--duration', type=str,
                         choices=['day', 'fill_or_kill', 'immediate_or_cancel',
                                  'good_till_cancel', 'good_till_time',
                                  'at_the_opening', 'at_the_close'])
    aparser.add_argument('-q', '--qty', type=str)
    aparser.add_argument('-l', '--limit-price', type=str)

    args = aparser.parse_args()
    loglevel = getattr(logging, args.log_level.upper())
    logging.basicConfig(filename=None, format=args.log_format,
                        level=loglevel)

    proc = broker_proc(args.path)

    con_id = connect(proc, args.gw_url)

    #t = threading.Thread(target=read_out, name='get_stdout', args=(proc,))
    #t.start()

    ssh_client = connect_gw(args.gw_url)

    host_list = resolve_hosts(blocking_hosts, args.gw_url)

    print('connection established with {}'.format(con_id))

    time.sleep(CON_TIMEOUT)

    if args.type == 'market':
        order_id = place_market(proc, con_id, args.user, args.acc,
                            args.instrument, args.side,
                            args.qty, duration=args.duration)
    elif args.type == 'limit':
        order_id = place_limit(proc, con_id, args.user, args.acc,
                               args.instrument, args.side, args.qty,
                               args.duration, args.limit_price)
    else:
        pass

    time.sleep(PLACE_TIMEOUT)

    #tc = threading.Timer(0.005, cancel, args=(proc, con_id, order_id, args.user))
    cancel(proc, con_id, order_id, args.user)

    drop_con(ssh_client, host_list)

    #for i in range(5):
    #    time.sleep(0.1)
    #    cancel(proc, con_id, order_id, args.user)

    time.sleep(TIMEOUT)

    cancel(proc, con_id, order_id, args.user)

    enable_con(ssh_client, host_list)

    #time.sleep(TIMEOUT)

    disc_gw(ssh_client)

    disconnect(proc, con_id)

    try:
        terminate_proc(proc)
    except subprocess.TimeoutExpired as err:
        logging.debug('error during termination: {}'.format(err))
