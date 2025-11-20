from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class BaseEntity:
    """
    Базовая сущность для всех Entity.
    Поддерживает:
    - Преобразование Pydantic или dataclass схем в Entity (from_schema)
    - Сериализацию в словарь без None полей (to_dict)
    """

    # Защита от циклов при рекурсивной сериализации
    _visited: set[int] = field(default_factory=set, init=False, repr=False, compare=False)

    def to_dict(self) -> dict:
        def convert(value: Any, visited: set[int]) -> Any:
            if value is None:
                return None
            if isinstance(value, BaseEntity):
                obj_id = id(value)
                if obj_id in visited:
                    return None  # предотвращаем бесконечную рекурсию
                visited.add(obj_id)
                return value.to_dict()
            elif isinstance(value, list):
                converted = [convert(v, visited) for v in value]
                return [v for v in converted if v is not None] or None
            elif isinstance(value, dict):
                converted = {k: convert(v, visited) for k, v in value.items()}
                return {k: v for k, v in converted.items() if v is not None} or None
            elif isinstance(value, datetime):
                return value.isoformat()
            else:
                return value

        return {k: v for k, v in ((k, convert(val, self._visited.copy())) for k, val in self.__dict__.items() if not k.startswith("_")) if v is not None}

    @classmethod
    def from_schema(cls, schema: Any) -> BaseEntity:
        """
        Создаёт Entity из Pydantic модели или dataclass схемы.
        Игнорирует unset/None значения.
        """
        if hasattr(schema, "model_dump"):
            data = schema.model_dump(exclude_unset=True)
        elif hasattr(schema, "dict"):
            data = schema.dict(exclude_unset=True)
        else:
            raise TypeError("Schema must be a Pydantic model or dataclass")

        allowed_fields = cls.__annotations__.keys()
        filtered = {k: v for k, v in data.items() if k in allowed_fields}
        return cls(**filtered)
