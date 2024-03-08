import math
import sqlite3

from datetime import datetime
from time import time
from app import app


def db_execute(database, sql):
  data = {
    'rows': []
  }

  try:
    with sqlite3.connect(app.config['DB_PATH'] + database) as conn:
      conn.create_function('LOG', 1, math.log)
      cursor = conn.execute(sql)

      if cursor.rowcount < 1:
        data['error'] = 'No results found.'

      for row in cursor:
        data['rows'].append(row)
      conn.commit()
  except sqlite3.Error as e:
    conn.rollback()
    print(e)
    data['error'] = e
  finally:
    conn.close()

  return data

# def get_pdfs_from_db(fields,limit=5,page=0):
#   data = {
#     'rows': [],
#   }
  
#   try:
#     with sqlite3.connect(app.config['DB_PATH'] + 'pdf.db') as conn:
#       cursor = conn.execute(f'SELECT {('?,' * len(fields))[:-1]}, ID FROM PDF ORDER BY ID DESC LIMIT {limit} OFFSET {page}', fields)
      
#       if cursor.rowcount < 1:
#         data['error'] = 'No results found.'

#       for row in cursor:
#         data['rows'].append(row)

#       conn.commit()
#   except sqlite3.Error as e:
#     conn.rollback()
#     print(e)
#     data['error'] = e
#   finally:
#     conn.close()

#   return data

def get_most_recents(limit=3, page=0):
  sql = """
    SELECT
    NAME, DATE, TITLE, AUTHORS, YEAR, MONTH, ABSTRACT, ID
    FROM PDF
    ORDER BY ID DESC LIMIT {} OFFSET {}
""".format(limit, page*limit)

  start_time = time()
  data = db_execute('pdf.db', sql)
  end_time = time()

  pdfs = []
  if data['error'] is not None:
    for row in data['rows']:
      pdfs.append({
        "pdf_name": row[0],
        "date"    : format(datetime.fromtimestamp(row[1]), '%d/%m/%Y'),
        "title"   : row[2],
        "authors" : row[3],
        "year"    : row[4],
        "month"   : row[5],
        "abstract": row[6],
        "id"      : row[7],
        "score"   : 0
      })

  return pdfs, end_time - start_time



def get_user_by_id(userid):
  sql = "SELECT userid, email, given_name, family_name, picture, allow_upload, allow_delete, view_history, saved_trs, user_type FROM USERS WHERE userid = '{}'".format(userid)
  data = db_execute('users.db',sql)
  if data['error'] is not None:
    user = {
      "email"         : data['rows'][0][1],
      "given_name"    : data['rows'][0][2],
      "family_name"   : data['rows'][0][3],
      "picture"       : data['rows'][0][4],
      "allow_upload"  : data['rows'][0][5],
      "allow_delete"  : data['rows'][0][6],
      "view_history"  : data['rows'][0][7],
      "saved_trs"     : data['rows'][0][8],
      "user_type"     : data['rows'][0][9],
    }

    return user
  
  return 'Cannot login'

def upsert_user(credentials):
  sql = """
      INSERT INTO USERS(userid, email, given_name, family_name, picture)
      VALUES ('{userid}', '{email}', '{given_name}', '{family_name}', '{picture}')
      ON CONFLICT (userid) DO UPDATE SET
      given_name = excluded.given_name,
      family_name = excluded.family_name,
      picture = excluded.picture
      WHERE userid = '{userid}'
    """.format(
      userid = credentials.get('userid'),
      email = credentials.get('email'),
      given_name = credentials.get('given_name'),
      family_name = credentials.get('family_name'),
      picture = credentials.get('picture')
    )
  db_execute('users.db',sql)
  return get_user_by_id(credentials.get('userid'))
