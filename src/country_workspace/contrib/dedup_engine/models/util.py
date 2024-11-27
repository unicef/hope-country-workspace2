from datetime import datetime
from enum import Enum
from typing import Self, Type, TypeVar

from pydantic import ConfigDict

T = TypeVar("T")


class DeduplicationSetStatus(Enum):
    CLEAN = "Clean"
    DIRTY = "Dirty"

    @property
    def description(self) -> str:
        descriptions = {
            DeduplicationSetStatus.CLEAN: "Deduplication set is created or already processed",
            DeduplicationSetStatus.DIRTY: "Deduplication set needs processing",
        }
        if self not in descriptions:
            raise ValueError(f"Description for status {self} is not defined.")
        return descriptions[self]

    @classmethod
    def get_description(cls, status: Self) -> str:
        if not isinstance(status, cls):
            raise ValueError(f"Invalid status: {status}")
        return status.description


def merge_configs(*mixins) -> Type[T]:
    def decorator(cls: Type[T]) -> Type[T]:
        merged_config = {}
        for mixin in mixins:
            for k, v in mixin.get_config().items():
                if k not in merged_config:
                    merged_config[k] = v
                elif isinstance(v, dict) and isinstance(merged_config[k], dict):
                    merged_config[k].update(v)
                else:
                    raise ValueError(f"Conflict in config key '{k}' for {cls.__name__}")

        cls.model_config = ConfigDict(**merged_config)
        return cls

    return decorator


class DatetimeEncoderMixin:
    @staticmethod
    def get_config() -> ConfigDict:
        return ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


class StatusEncoderMixin:
    @staticmethod
    def get_config() -> ConfigDict:
        return ConfigDict(json_encoders={DeduplicationSetStatus: lambda v: v.value})
