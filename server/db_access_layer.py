import os
from urllib.parse import urlparse

import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor


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
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if not values:
                cursor.execute(query)
            else:
                cursor.execute(query, values)
            result = cursor.fetchall()
        return result

    def insert(self, table_name, column_names, values):
        """
        Insert value or values in table with table_name.
        :param table_name: string, name of table;
        :param column_names: list of str, names of columns of table;
        :param values: list of dict or just dict with data to be inserted;
        :return: result of inserting - list of identifications of created objects.
        """
        data = []
        values_template = ''
        # If a list of records is received
        if type(values) == list:
            data = [tuple([value[column] for column in column_names]) for value in values]
            values_template = ','.join(['%s'] * len(values))
        elif type(values) == dict:
            data = tuple([values[column] for column in column_names])
            values_template = '({})'.format(','.join(['%s'] * len(column_names)))
        # Create sql query
        sql_q = 'INSERT INTO {} ({}) VALUES {} RETURNING id;'.format(table_name, ','.join(column_names),
                                                                     values_template)
        result = self.__execute_sql(query=sql_q, values=data)
        return result

    def update(self, table_name, values, id):
        """
        Update some fields of record with identificator = id.
        :param table_name:
        :param column_names:
        :param values:
        :return:
        """
        data = tuple([values[column] for column in values.keys()])
        values_template = ','.join(['{} = %s'.format(column) for column in values.keys()])
        # Create sql query
        sql_q = 'UPDATE {} SET {} WHERE id = {} RETURNING id;'.format(table_name, values_template, id)
        result = self.__execute_sql(query=sql_q, values=data)
        return result

    def delete(self, table_name, id, returning='id'):
        """
        Delete one record from the table.
        :param returning: str, field of deleted object that should be returned after deleting.
        :param id: deleting record's id.
        :param table_name: str, name of table.
        :return: return True if record is deleted and False if an error has occurred.
        """
        sql_q = 'DELETE FROM {} WHERE id = %s RETURNING {};'.format(table_name, returning)
        result = self.__execute_sql(query=sql_q, values=(id,))
        return result

    def select(self, table_name, columns='*', condition=None, order=tuple()):
        """
        Get records from a table in a specific order when a given condition is met.
        :param condition: dict of conditions where key(column_name)=value(record_value)
        :param table_name: str, name of table.
        :param columns: str, columns name that should be selected.
        :param order: tuple of two str, where first element - column name, second - 'asc' or 'desc'.
        :return: list of tuples with records data.
        """
        if columns == '':
            columns = '*'
        sql_q = 'SELECT {} FROM {}'.format(columns, table_name)
        if condition is not None:
            conditions = ' AND '.join(['{}={}'.format(column, condition[column]) for column in condition.keys()])
            sql_q += ' WHERE ' + conditions
        if order is not None:
            if len(order) == 2:
                sql_q += ' ORDER BY {} {}'.format(order[0], order[1])

        return self.__execute_sql(sql_q)

    def close(self):
        """
        Close db connection.
        """
        self.conn.close()

    def complete_transaction(self):
        self.conn.commit()
