from .base import BaseEntry
from dataclasses import dataclass, field


@dataclass
class PersonEntry(BaseEntry):
    """
    Содержит информацию об одной записи из таблицы person.
    """
    full_name: str = field(default='')

    @staticmethod
    def get_table_name() -> str:
        return 'person'
