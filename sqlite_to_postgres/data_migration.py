import sqlite3
import psycopg2
import os
from contextlib import contextmanager
from dotenv import load_dotenv
from dataclasses import astuple
from database_entries.base import BaseEntry
from database_entries.film_work_entry import FilmWorkEntry

load_dotenv()


class DataMigration:
    """
    Переносит данные из одной базы данных в другую.

    Опеределения:
    Источник - база данных, из которой извлекаются данные. В коде будет обозначена как source.
    Цель - база данных, в которую добавляются данные. В коде будет обозначена как target.

    """
    SOURCE_PATH = os.environ.get('SOURCE_PATH')
    DNS = {
        'dbname': os.environ.get('TARGET_NAME'),
        'user': os.environ.get('TARGET_USER'),
        'password': os.environ.get('TARGET_PASSWORD'),
        'host': os.environ.get('TARGET_HOST'),
        'port': 5432,
        'options': '-c search_path=content',
    }

    def __init__(self, table: BaseEntry) -> None:
        """
        Конструктор.
        """
        self.table = table
        self.table_name = table.get_table_name()
        self.column_names = table.get_column_names()
        self.column_count = table.get_column_count()

    def get_data(self):
        """
        Собирает данные из базы данных источник.
        """
        with DataMigration.get_connection() as conn:
            curs = conn.cursor()
            column_names = self.column_names.replace('created', 'created_at')

            fetch_query = f'SELECT {column_names} FROM {self.table_name};'
            curs.execute(fetch_query)
            while True:
                rows = curs.fetchmany(10)
                if not rows: break
                yield rows

    @classmethod
    @contextmanager
    def get_connection(cls):
        conn = sqlite3.connect(cls.SOURCE_PATH)
        #conn.row_factory = sqlite3.Row

        yield conn
        conn.close()

    def load_data(self):
        """
        Загружает данные в цель.
        """
        with psycopg2.connect(**self.DNS) as conn, conn.cursor() as cursor:
            for data in self.get_data():

                args = ','.join(
                    cursor.mogrify(
                        f'({self.column_count}, NOW())',
                        astuple(self.table(*item))
                    ).decode('utf-8') for item in data
                )

                insert_query = f"""
                INSERT INTO content.{self.table_name} ({self.column_names}, modified)
                VALUES {args}
                ON CONFLICT (id) DO NOTHING;;
                """
                cursor.execute(insert_query)


if __name__ == '__main__':
    test = DataMigration(FilmWorkEntry)
    test.load_data()
