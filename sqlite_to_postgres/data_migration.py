import sqlite3
import io
import psycopg2
import os
from contextlib import contextmanager
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

    def __init__(self) -> None:
        """
        Конструктор.
        """
        pass

    def get_data(self):
        """
        Собирает данные из базы данных источник.
        """
        with DataMigration.get_connection() as conn:
            # Получаем курсор
            curs = conn.cursor()
            # Формируем запрос. Внутри execute находится обычный SQL-запрос
            curs.execute("SELECT * FROM film_work;")
            # Получаем данные
            data = curs.fetchall()
            print(dict(data[0]))

    @classmethod
    @contextmanager
    def get_connection(cls):
        # Устанавливаем соединение с БД
        conn = sqlite3.connect(cls.SOURCE_PATH)

        # По-умолчанию SQLite возвращает строки в виде кортежа значений.
        # Эта строка указывает, что данные должны быть в формате «ключ-значение»
        conn.row_factory = sqlite3.Row

        yield conn
        conn.close()

    def load_data(self):
        """
        Загружает данные в цель.
        """
        dsn = {
            'dbname': os.environ.get('TARGET_NAME'),
            'user': os.environ.get('TARGET_USER'),
            'password': os.environ.get('TARGET_PASSWORD'),
            'host': os.environ.get('TARGET_HOST'),
            'port': 5432,
            'options': '-c search_path=content',
        }

        with psycopg2.connect(**dsn) as conn, conn.cursor() as cursor:
            # Множественный insert
            # Обращаем внимание на подготовку параметров для VALUES через cursor.mogrify
            # Это позволяет без опаски передавать параметры на вставку
            # mogrify позаботится об экранировании и подстановке нужных типов
            # Именно поэтому можно склеить тело запроса с подготовленными параметрами
            data = [
                ('b8531efb-c49d-4111-803f-725c3abc0f5e', 'Василий Васильевич'),
                ('2d5c50d0-0bb4-480c-beab-ded6d0760269', 'Пётр Петрович')
            ]
            args = ','.join(cursor.mogrify("(%s, %s)", item).decode() for item in data)
            cursor.execute(f"""
            INSERT INTO content.temp_table (id, name)
            VALUES {args}
            """)



if __name__ == '__main__':
    test = DataMigration()
    test.get_data()
    test.load_data()
