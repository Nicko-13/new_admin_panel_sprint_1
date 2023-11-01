import sqlite3
from datetime import datetime

import psycopg2

from sqlite_to_postgres.config import SOURCE_PATH, TARGET_DNS
from sqlite_to_postgres.data_migration import DataMigration
from sqlite_to_postgres.database_entries.film_work_entry import FilmWorkEntry
from sqlite_to_postgres.database_entries.genre_entry import GenreEntry
from sqlite_to_postgres.database_entries.genre_film_work_entry import GenreFilmWorkEntry
from sqlite_to_postgres.database_entries.person_entry import PersonEntry
from sqlite_to_postgres.database_entries.person_film_work_entry import PersonFilmWorkEntry


def test_migration() -> None:
    """
    Проверяет, что количество записей в базе совпадает и что каждая запись совпадает между собой.
    """
    test_instance = DataMigration()

    with sqlite3.connect(SOURCE_PATH) as source_conn, psycopg2.connect(**TARGET_DNS) as target_conn:
        for entry_class in [
            FilmWorkEntry,
            PersonEntry,
            GenreEntry,
            PersonFilmWorkEntry,
            GenreFilmWorkEntry,
        ]:
            for source_data, target_data in zip(
                test_instance.get_data(source_conn.cursor(), entry_class),
                test_instance.get_data(target_conn.cursor(), entry_class, database='target'),
            ):
                for i in range(len(source_data)):
                    for j in range(len(source_data[0])):
                        source, target = source_data[i][j], target_data[i][j]

                        if isinstance(target, datetime):
                            target = target.strftime('%Y-%m-%d %H:%M:%S.%f%z').split('.')[0]
                            source = source.split('.')[0]

                        assert source == target
