import os
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras


class DB:
    def __init__(self):
        """
        Create connection to db.
        """
        url = urlparse(os.environ.get('DATABASE_URL'))
        db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
        try:
            conn = psycopg2.connect(db)
        except psycopg2.OperationalError as e:
            print('Unable to connect\n{}'.format(e))
        else:
            self.conn = conn

    def __execute_sql(self, query, values=None):
        """
        Execute sql query and return the result of query.
        :param query: query template string with '%s' instead of value.
        :param values: values (if there is need) of sql query.
        :return: sql query result.
        """
        result = []
        with self.conn.cursor() as cursor:
            if not values:
                cursor.execute(query)
            else:
                cursor.execute(query, values)
            result = cursor.fetchall()
        return result

    def insert(self, table_name, columns_name, values):
        """
        Insert value or values in table with table_name.
        :param table_name: string, name of table;
        :param columns_name: list of str, names of columns of table;
        :param values: list of dict or just dict with data to be inserted;
        :return: result of inserting - list of identifications of created objects.
        """
        data = []
        values_template = ''
        # If a list of records is received
        if type(values) == list:
            data = [tuple([value[column] for column in columns_name]) for value in values]
            values_template = ','.join(['%s'] * len(values))
        elif type(values) == dict:
            data = tuple([values[column] for column in columns_name])
            values_template = '({})'.format(','.join(['%s'] * len(columns_name)))
        # Create sql query
        sql_q = 'INSERT INTO {} ({}) VALUES {} RETURNING id;'.format(table_name, ','.join(columns_name),
                                                                     values_template)
        result = self.__execute_sql(query=sql_q, values=data)
        return result

    def close(self):
        """
        Close db connection.
        """
        self.conn.close()

    def complete_transaction(self):
        self.conn.commit()
