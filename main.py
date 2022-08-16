import os

import psycopg2

from constans import DATABASES

dirname = os.path.dirname(__file__)


def create_func(query):
    try:
        connection = psycopg2.connect(
            host=DATABASES['HOST'],
            user=DATABASES['USER'],
            password=DATABASES['PASSWORD'],
            database=DATABASES['NAME']
        )

        connection.autocommit = True

        with connection.cursor() as cur:
            cur.execute(query)
    except Exception as exc:
        print('Error while working with Postgresql', exc)
    finally:
        if connection:
            connection.close()
            print('[INFO] Postgresql connection closed')


create_table = '''
CREATE TABLE IF NOT EXISTS cats(
id SERIAL PRIMARY KEY,
name VARCHAR(50) DEFAULT 'Cat',
breed VARCHAR(100) DEFAULT 'Outbred'
);
'''
complete_table = '''
COPY cats FROM '{0}/cats.csv'
DELIMITER ',' CSV HEADER;
'''.format(dirname)

if __name__ == '__main__':
    create_func(create_table)
    print('[INFO] Table created successfully')
    create_func(complete_table)
    print('[INFO] Table filled with data successfully')
