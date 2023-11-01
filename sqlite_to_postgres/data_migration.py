import sqlite3
import logging
from dataclasses import astuple
from sqlite3.dbapi2 import Cursor
from typing import Generator, Optional, Type, Union

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor

from sqlite_to_postgres.database_entries import (
    BaseEntry,
    FilmWorkEntry,
    GenreEntry,
    GenreFilmWorkEntry,
    PersonEntry,
    PersonFilmWorkEntry,
)
from sqlite_to_postgres import config

load_dotenv()
logging.basicConfig(format='%(asctime)s [%(levelname)s][Method:%(funcName)s]: %(message)s', datefmt='%d-%b-%y %H:%M:%S')


class DataMigration:
    """
    Переносит данные из одной базы данных в другую.

    Опеределения:
    Источник - база данных, из которой извлекаются данные. В коде будет обозначена как source.
    Цель - база данных, в которую добавляются данные. В коде будет обозначена как target.

    """

    def get_data(
        self,
        cursor: Union[Cursor, NamedTupleCursor],
        entry_class: Type[BaseEntry],
        database: Optional[str] = 'source',
    ) -> Generator[list[tuple[str]], None, None]:
        """
        Собирает данные из базы данных. Каждая запись представляет собой картеж.
        Картежи содержатся в массиве.

        :param cursor: Курсор базы данных.
        :param entry_class: Класс, представляющий одну запись в базе данных.
        :param database: База данных, из которой извлекаются данные.

        :yield: массив записей из базы данных длинной self.BATCH_SIZE.
        """
        column_names = entry_class.get_column_names()
        if database == 'source':
            # в базе данных источник и цель название поля различаются.
            column_names = column_names.replace('created', 'created_at')
        table_name = entry_class.get_table_name()

        cursor.execute(f'SELECT {column_names} FROM {table_name};')
        while rows := cursor.fetchmany(config.BATCH_SIZE):
            yield rows

    def load_data(
        self,
        batch: list[tuple[str]],
        cursor: Union[Cursor, NamedTupleCursor],
        entry_class: Type[BaseEntry],
    ) -> None:
        """
        Загружает данные в базу данных.

        :param batch: Массив записей для вставки в базу данных длинной.
        :param cursor: Курсор базы данных.
        :param entry_class: Класс, представляющий одну запись в базе данных.
        """
        table_name = entry_class.get_table_name()
        column_names = entry_class.get_column_names()
        column_formatting_template = entry_class.get_column_formatting_template()

        args = ','.join(
            cursor.mogrify(
                f'({column_formatting_template}, NOW())',
                astuple(entry_class(*item)),
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
        with sqlite3.connect(config.SOURCE_PATH) as source_conn, psycopg2.connect(**config.TARGET_DNS) as target_conn:
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()

            for entry_class in [
                FilmWorkEntry,
                PersonEntry,
                GenreEntry,
                PersonFilmWorkEntry,
                GenreFilmWorkEntry,
            ]:
                try:
                    for batch in self.get_data(source_cursor, entry_class):
                        self.load_data(batch, target_cursor, entry_class)
                except Exception as e:
                    logging.error(e)

        source_conn.close()
        target_conn.close()
