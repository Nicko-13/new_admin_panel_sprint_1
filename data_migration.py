import sqlite3
from contextlib import contextmanager


@contextmanager
def conn_context(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


db_path = 'sqlite_to_postgres/db.sqlite'  # path should be in environmental variable
with conn_context(db_path) as conn:
    curs = conn.cursor()
    curs.execute("SELECT * FROM film_work;")
    data = curs.fetchall()  # should be batch data extraction
    print(dict(data[0]))
