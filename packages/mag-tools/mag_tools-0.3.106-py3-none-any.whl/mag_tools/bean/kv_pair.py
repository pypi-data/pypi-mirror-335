from dataclasses import dataclass
from typing import Generic, TypeVar

K = TypeVar('K')
V = TypeVar('V')

@dataclass
class KvPair(Generic[K, V]):
    """
    Key与Value对

    :param K: Key
    :param V: Value
    """
    k: K
    v: V