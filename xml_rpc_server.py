import logging
from multiprocessing import Queue, Process
from xmlrpc.server import SimpleXMLRPCServer

import psycopg2

from constans import DATABASES

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('query_journal.txt', mode='a')
handler.setFormatter(formatter)
logger.addHandler(handler)


connection = psycopg2.connect(
    host=DATABASES['HOST'],
    user=DATABASES['USER'],
    password=DATABASES['PASSWORD'],
    database=DATABASES['NAME']
)

connection.autocommit = True

server = SimpleXMLRPCServer(('127.0.0.1', 8000), allow_none=True)


def read(id, q):
    with connection.cursor() as cur:
        cur.execute('''
            SELECT * FROM cats WHERE id = '{0}';
        '''.format(id))
        q.put(cur.fetchone())


def save(id: int, field_name: str, data: str, q: Queue):
    with connection.cursor() as cur:
        cur.execute('''
            INSERT INTO cats (id, {1}) VALUES
            ('{0}', '{2}')
            ON CONFLICT (id) DO UPDATE
            SET {1} = '{2}'
            RETURNING *;
        '''.format(id, field_name, data))
        q.put(cur.fetchone())


def multifunction(id1: int, id2: int, field_name: str, data: str):
    q = Queue()
    p = Process(target=read, args=(id1, q))
    p.start()
    p1 = Process(target=save, args=(id2, field_name, data, q))
    p1.start()
    logger.info(q.get())
    logger.info(q.get())
    p.join()
    p1.join()


server.register_multicall_functions()
server.register_function(read, 'read')
server.register_function(save, 'save')
server.register_function(multifunction, 'multifunction')


if __name__ == '__main__':
    try:
        print('Serving...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
