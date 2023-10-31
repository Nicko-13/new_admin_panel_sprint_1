import uuid
from datetime import datetime
from dataclasses import dataclass, field, fields
from abc import ABC, abstractmethod


@dataclass
class BaseEntry(ABC):
    """
    Абстрактный базовый класс для одной записи в базе данных.

    Так как этот класс содержит поля с дефолтными значениями, каждое поля подкласса также должно иметь дефолтное
    значение.
    """
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created: datetime = field(default=None)

    @staticmethod
    @abstractmethod
    def get_table_name() -> str:
        """
        Возвращает название таблицы, к которой принадлежит запись.
        """
        pass

    @classmethod
    def get_column_names(cls) -> str:
        """
        Возвращает название колонок записи.
        """
        return ', '.join(field_.name for field_ in fields(cls))

    @classmethod
    def get_column_formatting_template(cls) -> str:
        """
        Возвращает темплейт для вставки названия колонок в SQL запрос.
        """
        return ', '.join('%s' for _ in range(len(fields(cls))))
