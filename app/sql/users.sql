-- CREATE TABLE USERS (
--   ID INTEGER PRIMARY KEY AUTOINCREMENT,
--   IP             TEXT    NOT NULL,
--   NB_CONNECTIONS INT     DEFAULT 0
-- );

DROP TABLE IF EXISTS USERS;
CREATE TABLE IF NOT EXISTS USERS (
  userid            TEXT PRIMARY KEY,
  email             TEXT UNIQUE NOT NULL,
  given_name        TEXT NOT NULL,
  family_name       TEXT,
  picture           TEXT,
  department        TEXT DEFAULT 'ICS',
  college           TEXT DEFAULT 'CAS',
  campus            TEXT DEFAULT 'UPLB',
  user_type         TEXT DEFAULT 'STUDENT',
  allow_upload      BOOLEAN DEFAULT FALSE,
  allow_delete      BOOLEAN DEFAULT FALSE,
  view_history      TEXT DEFAULT '[]',
  saved_trs         TEXT DEFAULT '[]',
  created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);