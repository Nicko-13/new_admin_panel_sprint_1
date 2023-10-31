import os
import sqlite3
from contextlib import contextmanager
from dataclasses import astuple
from datetime import datetime
from sqlite3.dbapi2 import Connection
from typing import Generator, Type

import psycopg2
from database_entries.base import BaseEntry
from database_entries.film_work_entry import FilmWorkEntry
from database_entries.genre_entry import GenreEntry
from database_entries.genre_film_work_entry import GenreFilmWorkEntry
from database_entries.person_entry import PersonEntry
from database_entries.person_film_work_entry import PersonFilmWorkEntry
from dotenv import load_dotenv

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

    def get_source_data(self) -> Generator[list[tuple[str]], None, None]:
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

    def get_target_data(self) -> Generator[list[tuple[str]], None, None]:
        """
        Собирает данные из базы данных цель. Каждая запись представляет собой картеж.
        Картежи содержатся в массиве.

        :yield: массив записей из базы данных длинной self.BATCH_SIZE.
        """
        with psycopg2.connect(**self.TARGET_DNS) as conn, conn.cursor() as cursor:
            cursor.execute(f'SELECT {self.column_names} FROM {self.table_name};')
            while True:
                rows = cursor.fetchmany(self.BATCH_SIZE)
                if not rows:
                    break
                yield rows

    def load_data(self) -> None:
        """
        Загружает данные в цель.
        """
        with psycopg2.connect(**self.TARGET_DNS) as conn, conn.cursor() as cursor:
            for data in self.get_source_data():
                args = ','.join(
                    cursor.mogrify(
                        f'({self.column_formatting_template}, NOW())',
                        astuple(self.entry(*item)),
                    ).decode('utf-8')
                    for item in data
                )

                insert_query = f"""
                INSERT INTO content.{self.table_name} ({self.column_names}, modified)
                VALUES {args}
                ON CONFLICT (id) DO NOTHING;;
                """
                cursor.execute(insert_query)

    def test_migration(self) -> None:
        """
        Проверяет, что количество записей в базе совпадает и что каждая запись совпадает между собой.
        """
        for source_data, target_data in zip(
            self.get_source_data(),
            self.get_target_data(),
        ):
            for i in range(len(source_data)):
                for j in range(len(source_data[0])):
                    source, target = source_data[i][j], target_data[i][j]

                    if isinstance(target, datetime):
                        target = target.strftime('%Y-%m-%d %H:%M:%S.%f%z').split('.')[0]
                        source = source.split('.')[0]

                    assert source == target


if __name__ == '__main__':
    for table in [
        FilmWorkEntry,
        PersonEntry,
        GenreEntry,
        PersonFilmWorkEntry,
        GenreFilmWorkEntry,
    ]:
        migration = DataMigration(table)
        migration.load_data()
        migration.test_migration()
