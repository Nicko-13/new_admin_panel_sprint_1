from dataclasses import dataclass, field

from .base import BaseEntry


@dataclass
class PersonEntry(BaseEntry):
    """
    Содержит информацию об одной записи из таблицы person.
    """

    full_name: str = field(default='')

    @staticmethod
    def get_table_name() -> str:
        return 'person'
