import uuid
from datetime import datetime
from dataclasses import dataclass, field, fields
from abc import ABC, abstractmethod


@dataclass
class BaseEntry(ABC):
    """
    Абстрактный базовый класс для одной записи в базе данных.
    """
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created: datetime = field(default=None)

    @staticmethod
    @abstractmethod
    def get_table_name():
        pass

    @classmethod
    def get_column_names(cls) -> str:
        """
        Возвращает название колонок в том порядке, в котором они должны быть в базе данных цель.
        """
        return ', '.join(field_.name for field_ in fields(cls))

    @classmethod
    def get_column_count(cls) -> str:
        return ', '.join('%s' for _ in range(len(fields(cls))))
