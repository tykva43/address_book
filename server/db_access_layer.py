import os
from urllib.parse import urlparse

import psycopg2


class DB:
    def __init__(self):
        url = urlparse(os.environ.get('DATABASE_URL'))
        db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
        try:
            conn = psycopg2.connect(db)
        except psycopg2.OperationalError as e:
            print('Unable to connect\n{}'.format(e))
        else:
            self.conn = conn

    def __execute_sql(self, query, values=None, many=False):
        result = []
        with self.conn.cursor() as cursor:
            if many:
                psycopg2.extras.execute_values(
                    cursor, query, values, fetch=True)
            else:
                if not values:
                    cursor.execute(query)
                else:
                    cursor.execute(query, values)
            print(cursor.fetchall())
            self.conn.commit()
        return result

    def insert(self, table_name, columns_name, values):
        """
        :param table_name: string, name of table;
        :param columns_name: list of str, names of columns of table;
        :param values: list of dict with inserting data;
        :return: result of inserting (True if data was inserted or False).
        """
        data = [tuple([value[column] for column in columns_name]) for value in values]
        values_template = ','.join('%s' * len(columns_name))
        sql_req = 'INSERT INTO {}({}) VALUES {}'.format(table_name, ','.join(columns_name), values_template)
        result = self.__execute_sql(query=sql_req, values=data, many=True)
        return result is not None

    def close(self):
        self.conn.close()
