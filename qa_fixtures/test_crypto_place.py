#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from test_crypto_cancel import *

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
    aparser.add_argument('-a', '--acc', type=str, nargs='?')
    aparser.add_argument('-i', '--instrument', type=str, nargs='?')
    aparser.add_argument('-s', '--side', type=str,
                         choices=['buy', 'sell'], nargs='?')
    aparser.add_argument('-t', '--type', type=str, choices=['market', 'limit',
                                                            'stop', 'stop_limit',
                                                            'twap', 'iceberg',
                                                            'trailing_stop'],
                         nargs='?')
    aparser.add_argument('-d', '--duration', type=str,
                         choices=['day', 'fill_or_kill', 'immediate_or_cancel',
                                  'good_till_cancel', 'good_till_time',
                                  'at_the_opening', 'at_the_close'], nargs='?')
    aparser.add_argument('-q', '--qty', type=str, nargs='?')
    aparser.add_argument('-l', '--limit-price', type=str, nargs='?')

    args = aparser.parse_args()
    loglevel = getattr(logging, args.log_level.upper())
    logging.basicConfig(filename=None, format=args.log_format,
                        level=loglevel)

    if re.match(r'.*globitex.*', args.gw_url, flags=re.IGNORECASE):
        brokeraccount_name = 'NEL939A01'
    else:
        brokeraccount_name = None
    proc = broker_proc(args.path)
    t = threading.Thread(target=read_out, name='get_stdout', args=(proc,))
    con_id = connect(proc, args.gw_url)
    t.start()

    host_list = resolve_hosts(blocking_hosts, args.gw_url)

    time.sleep(3)

    placed = list()
    for i in range(10):
        order_id = place_limit(proc, con_id=con_id, username=args.user, acc=args.acc,
                               instrument=args.instrument, side=args.side,
                               qty=args.qty, duration=args.duration,
                               limit_price=(float(args.limit_price) + i * 0.0001),
                               brokerAccount_name=brokeraccount_name)
        placed.append(order_id)
        print(order_id)

    time.sleep(5)

    for oid in placed:
        cancel(proc, con_id, oid, username=args.user)

    disconnect(proc, con_id)

    time.sleep(1)

    try:
        terminate_proc(proc)
    except subprocess.TimeoutExpired as err:
        logging.debug('{}'.format(err))
