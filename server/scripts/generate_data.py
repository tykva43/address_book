import os
from urllib.parse import urlparse

import psycopg2


def generate_rows(rows_num=500):
    # Connect to database
    url = urlparse(os.environ.get('DATABASE_URL'))
    db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
    conn = psycopg2.connect(db)

    cur = conn.cursor()
    create_f_sql = """CREATE OR REPLACE FUNCTION random_string(int, text)
                      RETURNS text
                      AS $$ 
                      SELECT array_to_string(
                          ARRAY (
                              SELECT substring($2 
                                FROM (random() *36)::int FOR 1)
                              FROM generate_series(1, $1) ), '' ) 
                      $$ LANGUAGE sql;"""
    cur.execute(create_f_sql)

    create_f_sql = """CREATE OR REPLACE FUNCTION random_email()
                      RETURNS text
                      AS $$ 
                      SELECT array_to_string(
                          ARRAY[
                               random_string(20, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '@', 
                               random_string(10, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), '.',
                               random_string(5, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                          ], '' )
                      $$ LANGUAGE sql;"""
    cur.execute(create_f_sql)

    create_f_sql = """CREATE OR REPLACE FUNCTION random_gender(items gender_type[])
                        RETURNS gender_type AS
                        $$
                        SELECT (items)[floor(random()*2+1)];
                        $$ LANGUAGE SQL;"""
    cur.execute(create_f_sql)

    create_f_sql = """CREATE OR REPLACE FUNCTION random_phone_type(items phone_type[])
                            RETURNS phone_type AS
                            $$
                            SELECT (items)[floor(random()*2+1)];
                            $$ LANGUAGE SQL;"""
    cur.execute(create_f_sql)

    create_f_sql = """CREATE OR REPLACE FUNCTION random_email_type(items email_type[])
                            RETURNS email_type AS
                            $$
                            SELECT (items)[floor(random()*2+1)];
                            $$ LANGUAGE SQL;"""
    cur.execute(create_f_sql)

    sql = "INSERT INTO users(id, name, photo_path, gender, born_at, address)  " \
          "SELECT id, " \
          "random_string(40, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), " \
          "md5('path'||id), " \
          "random_gender('{male,female}'::gender_type[]), " \
          "to_timestamp(random()*2147483647), " \
          "random_string(100, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') " \
          "FROM generate_series(1," + str(rows_num) + ") AS gs(id);"

    cur.execute(sql)
    conn.commit()

    sql = """INSERT INTO emails(id, user_id, email, type) 
       SELECT id, 
              floor(id/2),
              random_email(),
              random_email_type('{personal,work}'::email_type[]) 
       FROM generate_series(2,  """ + str(2*rows_num) + """) AS gs(id);"""

    cur.execute(sql)
    conn.commit()

    sql = """INSERT INTO phones(id, user_id, number, type) 
       SELECT id, 
              floor(id/2),
              random_string(19, '0123456789'),
              random_phone_type('{mobile,city}'::phone_type[])
       FROM generate_series(2,  """ + str(2*rows_num) + """) AS gs(id);"""

    cur.execute(sql)
    conn.commit()

    cur.close()
    conn.close()


if __name__ == '__main__':
    generate_rows()
