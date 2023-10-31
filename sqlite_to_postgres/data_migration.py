import os
import sqlite3
from dataclasses import astuple
from sqlite3.dbapi2 import Cursor
from typing import Generator, Optional, Type, Union

import psycopg2
from database_entries.base import BaseEntry
from database_entries.film_work_entry import FilmWorkEntry
from database_entries.genre_entry import GenreEntry
from database_entries.genre_film_work_entry import GenreFilmWorkEntry
from database_entries.person_entry import PersonEntry
from database_entries.person_film_work_entry import PersonFilmWorkEntry
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor

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

    def get_data(
        self,
        cursor: Union[Cursor, NamedTupleCursor],
        entry: Type[BaseEntry],
        database: Optional[str] = 'source',
    ) -> Generator[list[tuple[str]], None, None]:
        """
        Собирает данные из базы данных. Каждая запись представляет собой картеж.
        Картежи содержатся в массиве.

        :param cursor: Курсор базы данных.
        :param entry: Класс, представляющий одну запись в базе данных.
        :param database: База данных, из которой извлекаются данные.

        :yield: массив записей из базы данных длинной self.BATCH_SIZE.
        """
        column_names = entry.get_column_names()
        if database == 'source':
            # в базе данных источник и цель название поля различаются.
            column_names = column_names.replace('created', 'created_at')
        table_name = entry.get_table_name()

        cursor.execute(f'SELECT {column_names} FROM {table_name};')
        while True:
            rows = cursor.fetchmany(self.BATCH_SIZE)
            if not rows:
                break
            yield rows

    def load_data(
        self,
        batch: list[tuple[str]],
        cursor: Union[Cursor, NamedTupleCursor],
        entry: Type[BaseEntry],
    ) -> None:
        """
        Загружает данные в базу данных.

        :param batch: Массив записей для вставки в базу данных длинной.
        :param cursor: Курсор базы данных.
        :param entry: Класс, представляющий одну запись в базе данных.
        """
        table_name = entry.get_table_name()
        column_names = entry.get_column_names()
        column_formatting_template = entry.get_column_formatting_template()

        args = ','.join(
            cursor.mogrify(
                f'({column_formatting_template}, NOW())',
                astuple(entry(*item)),
            ).decode('utf-8')
            for item in batch
        )

        insert_query = f"""
        INSERT INTO content.{table_name} ({column_names}, modified)
        VALUES {args}
        ON CONFLICT (id) DO NOTHING;;
        """
        cursor.execute(insert_query)

    def migrate(self) -> None:
        """
        Получает данные из источника и вставляет их в цель.
        """
        with sqlite3.connect(self.SOURCE_PATH) as source_conn, psycopg2.connect(
            **self.TARGET_DNS
        ) as target_conn:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()

            for table in [
                FilmWorkEntry,
                PersonEntry,
                GenreEntry,
                PersonFilmWorkEntry,
                GenreFilmWorkEntry,
            ]:
                for batch in self.get_data(source_cursor, table):
                    self.load_data(batch, target_cursor, table)


if __name__ == '__main__':
    migration = DataMigration()
    migration.migrate()
