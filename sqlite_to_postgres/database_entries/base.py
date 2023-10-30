import uuid
from datetime import datetime
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class BaseEntry(ABC):
    """
    Абстрактный базовый класс для одной записи в базе данных.
    """
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    # Пустые значения для этих полей будут обрабатываться на уровне базы данных
    created: datetime = field(default=None)
    modified: datetime = field(default=None)

    @abstractmethod
    def get_fetch_query(self) -> str:
        """
        Возвращает базу SQL запроса для извлечения данных.
        """
        pass

    @abstractmethod
    def get_insert_query(self) -> str:
        """
        Возвращает базу SQL запроса для вставки данных.
        """
        pass
