import datetime
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')

@dataclass
class CacheEntry():
    id: str
    size: int
    result: Generic[T]
    created_at: datetime.datetime
