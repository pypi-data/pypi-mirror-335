from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import Any

from vajra.config.utils import get_all_subclasses


@dataclass(frozen=True)
class BasePolyConfig(ABC):

    @classmethod
    def create_from_type(cls, type_: Enum) -> Any:
        for subclass in get_all_subclasses(cls):
            if subclass.get_type() == type_:
                return subclass()
        raise ValueError(f"Invalid type: {type_}")

    @staticmethod
    def get_type() -> Enum:
        raise NotImplementedError
