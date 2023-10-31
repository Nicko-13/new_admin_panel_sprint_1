import sqlite3
import psycopg2
import os
from contextlib import contextmanager
from dotenv import load_dotenv
from dataclasses import astuple
from database_entries.base import BaseEntry
from database_entries.film_work_entry import FilmWorkEntry
from database_entries.genre_entry import GenreEntry
from database_entries.person_entry import PersonEntry
from database_entries.genre_film_work_entry import GenreFilmWorkEntry
from database_entries.person_film_work_entry import PersonFilmWorkEntry
from typing import Type, Generator
from sqlite3.dbapi2 import Connection

load_dotenv()


class DataMigration:
    """
    Переносит данные из одной базы данных в другую.

    Опеределения:
    Источник - база данных, из которой извлекаются данные. В коде будет обозначена как source.
    Цель - база данных, в которую добавляются данные. В коде будет обозначена как target.

    """
    SOURCE_PATH = os.environ.get('SOURCE_PATH')
    TARGET_DNS = {
        'dbname': os.environ.get('TARGET_NAME'),
        'user': os.environ.get('TARGET_USER'),
        'password': os.environ.get('TARGET_PASSWORD'),
        'host': os.environ.get('TARGET_HOST'),
        'port': 5432,
        'options': '-c search_path=content',
    }
    BATCH_SIZE = 100

    def __init__(self, entry: Type[BaseEntry]) -> None:
        """
        Конструктор.

        :param entry: Дата-класс, который представляет единичную запись одной из таблиц базы данных.
        """
        self.entry = entry
        self.table_name = entry.get_table_name()
        self.column_names = entry.get_column_names()
        self.column_formatting_template = entry.get_column_formatting_template()

    def get_data(self) -> Generator[list[tuple[str]], None, None]:
        """
        Собирает данные из базы данных источник. Каждая запись представляет собой картеж.
        Картежи содержатся в массиве.

        :yield: массив записей из базы данных длинной self.BATCH_SIZE.
        """
        with DataMigration.get_connection() as conn:
            curs = conn.cursor()
            # в базе данных источник и цель название поля различаются.
            column_names = self.column_names.replace('created', 'created_at')
            curs.execute(f'SELECT {column_names} FROM {self.table_name};')
            while True:
                rows = curs.fetchmany(self.BATCH_SIZE)
                if not rows:
                    break
                yield rows

    @classmethod
    @contextmanager
    def get_connection(cls) -> Generator[Connection, None, None]:
        """
        Устанавливает соединение с базой данных источник и передает его через генератор.

        :yield: соединение с базой данных источник.
        """
        conn = sqlite3.connect(cls.SOURCE_PATH)
        yield conn
        conn.close()

    def load_data(self) -> None:
        """
        Загружает данные в цель.
        """
        with psycopg2.connect(**self.TARGET_DNS) as conn, conn.cursor() as cursor:
            for data in self.get_data():

                args = ','.join(
                    cursor.mogrify(
                        f'({self.column_formatting_template}, NOW())',
                        astuple(self.entry(*item))
                    ).decode('utf-8') for item in data
                )

                insert_query = f"""
                INSERT INTO content.{self.table_name} ({self.column_names}, modified)
                VALUES {args}
                ON CONFLICT (id) DO NOTHING;;
                """
                cursor.execute(insert_query)


if __name__ == '__main__':
    for table in [FilmWorkEntry, PersonEntry, GenreEntry, PersonFilmWorkEntry, GenreFilmWorkEntry]:
        migration = DataMigration(table)
        migration.load_data()
