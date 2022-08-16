import logging
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


def read(id):
    with connection.cursor() as cur:
        cur.execute('''
            SELECT * FROM cats WHERE id = '{0}';
        '''.format(id))
        logger.info(cur.fetchone())


def save(id, field_name, data):
    with connection.cursor() as cur:
        cur.execute('''
            INSERT INTO cats (id, {1}) VALUES
            ('{0}', '{2}')
            ON CONFLICT (id) DO UPDATE
            SET {1} = '{2}'
            RETURNING *;
        '''.format(id, field_name, data))
        logger.info(cur.fetchone())


server.register_multicall_functions()
server.register_function(read, 'read')
server.register_function(save, 'save')


if __name__ == '__main__':
    try:
        print('Serving...')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
