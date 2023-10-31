import uuid
from dataclasses import dataclass, field

from .base import BaseEntry


@dataclass
class PersonFilmWorkEntry(BaseEntry):
    """
    Содержит информацию об одной записи из таблицы person_film_work.
    """

    person_id: uuid.UUID = field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)
    role: str = field(default='')

    @staticmethod
    def get_table_name() -> str:
        return 'person_film_work'
