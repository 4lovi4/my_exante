import argparse
from os import path
import subprocess
import threading
import queue
import json
import logging

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)s()] %(message)s"


class FeedProcess:

    def __init__(self, _client_path):
        self._path = _client_path
        self._command = 'java -classpath {} eu.exante.feed.client.cli.Main'.format(self._path)
        self.p = subprocess.Popen(self._command.split(' '),
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

    def close_client(self):
        self.p.terminate()


class RwThread(threading.Thread):

    def __init__(self, fd, q, _type='r'):
        super().__init__()
        self.queue = q
        self.fd = fd
        self._type = _type

    def run(self):
        logging.debug('thread {} started'.format(threading.get_ident()))
        if self._type == 'r':
            logging.debug('Reader started')
            for line in iter(self.fd.readline, ''):
                logging.debug('Reading {}: {}'.format(threading.get_ident(), line))
                self.queue.put(json.loads(line.decode('utf-8')))
        elif self._type == 'w':
            logging.debug('Writer started')
            while True:
                if self.fd.closed:
                    break
                logging.debug('writer queue size {}'.format(self.queue.qsize()))
                message = self.queue.get(timeout=30)
                logging.debug('Writing {}: {}'.format(threading.get_ident(), message))
                self.fd.write((json.dumps(message)).encode('utf-8'))
                self.queue.task_done()


if __name__ == '__main__':
    aparser = argparse.ArgumentParser()
    aparser.add_argument('-p', '--path', default='./feed-client.jar')
    aparser.add_argument('--log-level', default='info',
                         choices=('debug', 'warning', 'info', 'error', 'critical'))
    args = aparser.parse_args()

    logging.basicConfig(level=args.log_level.upper(), format=FORMAT)

    client_path = args.path

    if not path.exists(client_path):
        raise ValueError('wrong path to feed-client was provided')
        exit(1)

    stdout_queue = queue.Queue(maxsize=10)
    stdin_queue = queue.Queue(maxsize=10)

    feed_client_proc = FeedProcess(client_path)

    reader = RwThread(feed_client_proc.p.stdout, stdout_queue)
    writer = RwThread(feed_client_proc.p.stdin, stdin_queue, 'w')
    reader.start()
    writer.start()

    command = {'test': 'test'}

    stdin_queue.put(command)

    print('stdin queue size {}'.format(stdin_queue.qsize()))

    print('stdout queue size {}'.format(stdout_queue.qsize()))

    while not stdout_queue.empty():
        print(stdout_queue.get(timeout=5))
        queue.task_done()

    reader.join(timeout=5)
    print(reader.is_alive())
    writer.join(timeout=5)
    print(writer.is_alive())


