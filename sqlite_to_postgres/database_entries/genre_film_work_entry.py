import uuid
from dataclasses import dataclass, field

from .base import BaseEntry


@dataclass
class GenreFilmWorkEntry(BaseEntry):
    """
    Содержит информацию об одной записи из таблицы genre_film_work.
    """

    genre_id: uuid.UUID = field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)

    @staticmethod
    def get_table_name() -> str:
        return 'genre_film_work'
