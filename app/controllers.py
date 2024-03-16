import math
import sqlite3

from datetime import datetime
from time import time
from app import app


def db_execute(database, sql):
  data = {
    'error': None,
    'rows': [],
  }

  try:
    with sqlite3.connect(app.config['DB_PATH'] + database) as conn:
      conn.create_function('LOG', 1, math.log)
      cursor = conn.execute(sql)

      if cursor.rowcount == 0:
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

def get_pdfs_from_db(fields,filter=None,pdf_list=None,limit=5,page=0):
  sql = f"SELECT {', '.join(fields)} FROM pdf"
  if filter is not None:
    sql = sql + f" WHERE {filter['column']} = '{filter['value']}'"

  if pdf_list is not None:
    sublist = list(reversed(pdf_list.strip('][').split(', ')))[page*limit:(page*limit)+limit]

    if len(sublist) == 0:
      return [], 0

    # ORDER BY CASE so result will be in the same order of the list
    i = 1
    when_case = "CASE ID "
    for id in sublist:
      when_case += f" WHEN  {id} THEN {i} "
      i += 1
    when_case += " END"

    if filter is None:
      sql += " WHERE"
    else:
      sql += " AND"

    sql += f" ID IN ({', '.join(sublist)}) ORDER BY {when_case}"
  else:
    sql += f" ORDER BY ID DESC LIMIT {limit} OFFSET {page*limit}"
  
  start_time = time()
  data = db_execute('pdf.db', sql)
  end_time = time()

  pdfs = []
  if data['error'] is None:
    for row in data['rows']:
      pdf = {}
      for i in range(0,len(fields)):
        pdf[fields[i].lower()] = row[i]
      pdfs.append(pdf)

  return pdfs, end_time - start_time

def get_pdfs_by_words(words, limit=5, page=0):
  nb_pdf = count_pdf()

  pdfs = []
  sql = """
        SELECT A.PDF_ID, NAME, DATE, WORD, SUM(W_FREQ * LOG(TIDF)) * COUNT(WORD) AS SCORE, TITLE, AUTHORS, YEAR, MONTH, ABSTRACT
        FROM (SELECT PDF_ID, WORD, W_FREQ
              FROM FREQ
              WHERE WORD IN ('{}')) A
          INNER JOIN
             (SELECT ID AS P2, WORD AS W2, {} / COUNT(ID) AS TIDF
              FROM FREQ WHERE W2 IN ('{}')
              GROUP BY W2) B ON A.WORD = B.W2
          INNER JOIN
             (SELECT ID, NAME, DATE, TITLE, AUTHORS, YEAR, MONTH, ABSTRACT
              FROM PDF) C ON A.PDF_ID = C.ID
        GROUP BY A.PDF_ID
        ORDER BY SCORE DESC
        LIMIT {} OFFSET {}
      """.format("', '".join(words), str(float(nb_pdf)), "', '".join(words), limit, limit * page)

  start_time = time()
  data = db_execute('pdf.db', sql)
  end_time = time()

  if data['error'] is None:
    for row in data['rows']:
      pdfs.append({
        "id"       : row[0],
        "pdf_name" : row[1],
        "date"     : format(datetime.fromtimestamp(row[2]), '%d/%m/%Y'),
        "score"    : row[4] * 100,
        "title"    : row[5],
        "authors"  : row[6],
        "year"     : row[7],
        "month"    : row[8],
        "abstract" : row[9]
      })
  
  return pdfs, end_time - start_time

def count_pdf():
    sql = "SELECT COUNT(*) FROM PDF"
    data = db_execute('pdf.db', sql)
    return int(data['rows'][0][0])
  
# def get_most_recents(limit=5, page=0):
#   sql = """
#     SELECT
#     NAME, DATE, TITLE, AUTHORS, YEAR, MONTH, ABSTRACT, ID
#     FROM PDF
#     ORDER BY ID DESC LIMIT {} OFFSET {}
# """.format(limit, page*limit)

#   start_time = time()
#   data = db_execute('pdf.db', sql)
#   end_time = time()

#   pdfs = []
#   if data['error'] is None:
#     for row in data['rows']:
#       pdfs.append({
#         "pdf_name": row[0],
#         "date"    : format(datetime.fromtimestamp(row[1]), '%d/%m/%Y'),
#         "title"   : row[2],
#         "authors" : row[3],
#         "year"    : row[4],
#         "month"   : row[5],
#         "abstract": row[6],
#         "id"      : row[7],
#         "score"   : 0
#       })

#   return pdfs, end_time - start_time

# def get_pdfs_from_list(pdf_list, limit=5, page=0):

#   sublist = list(reversed(pdf_list.strip('][').split(', ')))[page*limit:(page*limit)+limit]

#   # ORDER BY CASE so result will be in the same order of the list
#   i = 1
#   when_case = "CASE ID "
#   for id in sublist:
#     when_case += f" WHEN  {id} THEN {i} "
#     i += 1
#   when_case += " END"

#   sql = """
#     SELECT
#     NAME, DATE, TITLE, AUTHORS, YEAR, MONTH, ABSTRACT, ID
#     FROM PDF
#     WHERE ID IN ({})
#     ORDER BY {}
# """.format(', '.join(sublist), when_case, limit, page*limit)

#   start_time = time()
#   data = db_execute('pdf.db', sql)
#   end_time = time()

#   pdfs = []
#   if data['error'] is None:
#     for row in data['rows']:
#       pdfs.append({
#         "pdf_name": row[0],
#         "date"    : format(datetime.fromtimestamp(row[1]), '%d/%m/%Y'),
#         "title"   : row[2],
#         "authors" : row[3],
#         "year"    : row[4],
#         "month"   : row[5],
#         "abstract": row[6],
#         "id"      : row[7],
#         "score"   : 0
#       })

#   return pdfs, end_time - start_time

def generate_bibtex(pdf_name):
  # conn = conn_to_db('pdf.db')
  # cursor = conn.execute("SELECT TITLE, AUTHORS, YEAR FROM PDF WHERE NAME='"+pdf_name+"'")

  sql = "SELECT TITLE, AUTHORS, YEAR FROM PDF WHERE NAME='"+pdf_name+"'"

  data = db_execute('pdf.db',sql)
  
  #fields = pdf_name.split("_")
  #cite_key=fields[len(fields)-1].split(".")[0]

  if data['error'] is None:
    for row in data['rows']: 
        fields = row[1].split(",")
        temp1=fields[0].split(" ")
        temp2=temp1[len(temp1)-1]
        temp3=row[0].split(" ")
        cite_key = temp2+row[2]+temp3[0]
        retval = "@techreport{"+cite_key+", title={"+row[0]+"}, author={" +row[1].replace(","," and ")+" }, year={"+row[2]+"}, institution={"+app.config['INSTITUTION']+"}, type={"+app.config['RESEARCH_GROUP']+" Technical Reports}}"

  return retval



def get_user_by_id(userid):
  sql = "SELECT userid, email, given_name, family_name, picture, allow_upload, allow_delete, view_history, saved_trs, user_type FROM USERS WHERE userid = '{}'".format(userid)
  data = db_execute('users.db',sql)
  if data['error'] is None:
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
  
  return data['error']

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

def toggle_favorite(userid, saved_trs):
  # lambda function turns saved_trs from list of str ['x','y','z'] to list of int [x,y,z]
  sql = "UPDATE users SET saved_trs = '{saved_trs}' WHERE userid = '{userid}'".format(saved_trs = list(map(lambda x : int(x), saved_trs)), userid = userid)
  db_execute('users.db',sql)
  return get_user_by_id(userid)

def update_view_history(userid, view_history):
  # lambda function turns saved_trs from list of str ['x','y','z'] to list of int [x,y,z]
  sql = "UPDATE users SET view_history = '{view_history}' WHERE userid = '{userid}'".format(view_history = list(map(lambda x : int(x), view_history)), userid = userid)
  db_execute('users.db',sql)
  return get_user_by_id(userid)
