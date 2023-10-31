from dataclasses import dataclass, field

from .base import BaseEntry


@dataclass
class GenreEntry(BaseEntry):
    """
    Содержит информацию об одной записи из таблицы genre.
    """

    name: str = field(default='')
    description: str = field(default='')

    @staticmethod
    def get_table_name() -> str:
        return 'genre'
