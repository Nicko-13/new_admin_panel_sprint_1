from .base import BaseEntry
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class FilmWorkEntry(BaseEntry):
    """
    Содержит информацию об одной записи из таблицы film_work.
    """
    title: str = field(default='')
    description: str = field(default='')
    creation_date: datetime = field(default='')
    rating: float = field(default=0.0)
    type: str = field(default='')

    @staticmethod
    def get_table_name() -> str:
        return 'film_work'
