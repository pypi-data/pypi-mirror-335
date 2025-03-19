import json
from decimal import Decimal
from datetime import datetime, date
from enum import Enum
from typing import Optional, Type, TypeVar, List, Dict, Any

from anytree import Node, RenderTree
from bean.easy_map import K, V
from model.base_enum import BaseEnum

T = TypeVar('T')
E = TypeVar('E')

class JsonParser:
    @staticmethod
    def to_string(json_src: str) -> str:
        return json.loads(json_src)

    @staticmethod
    def to_decimal(json_src: str) -> Optional[Decimal]:
        if not json_src:
            return None
        return Decimal(json.loads(json_src))

    @staticmethod
    def to_float(json_src: str) -> Optional[float]:
        if not json_src:
            return None
        return float(json.loads(json_src))

    @staticmethod
    def to_int(json_src: str) -> Optional[int]:
        if not json_src:
            return None
        return int(json.loads(json_src))

    @staticmethod
    def to_datetime(json_src: str) -> Optional[datetime]:
        if not json_src:
            return None
        return datetime.strptime(json.loads(json_src), '%Y-%m-%dT%H:%M:%S.%fZ')

    @staticmethod
    def to_bool(json_src: str) -> bool:
        json_str = JsonParser.to_string(json_src).lower()
        return json_str in ("y", "yes", "true", "t", "1")

    @staticmethod
    def to_enum(json_src: str, enum_type: Type[E]) -> Optional[E]:
        if not json_src or not issubclass(enum_type, Enum):
            return None
        enum_str = JsonParser.to_string(json_src)
        for member in enum_type:
            if member.name == enum_str or member.value == enum_str:
                return member
        return None

    @staticmethod
    def to_bean(json_src: str, clazz: Type[T]) -> Optional[T]:
        if not json_src or not clazz:
            return None
        return json.loads(json_src, object_hook=lambda d: clazz(**d))

    @staticmethod
    def to_list(json_src: str, clazz: Type[T]) -> List[T]:
        if not json_src:
            return []
        return json.loads(json_src, object_hook=lambda d: clazz(**d))

    @staticmethod
    def to_map(json_src: str, key_cls: Type[K], value_cls: Type[V]) -> Dict[K, V]:
        if not json_src:
            return {}
        data_map = json.loads(json_src)
        return {key_cls(key): value_cls(**value) if isinstance(value, dict) else value_cls(value) for key, value in data_map.items()}

    @staticmethod
    def to_easy_map(json_src: str, value_cls: Type[V]) -> Dict[str, V]:
        return JsonParser.to_map(json_src, str, value_cls)


    @staticmethod
    def to_tree(json_src: str, clazz: Type[T]) -> Node:
        if not json_src:
            return Node("root")

        data = json.loads(json_src)

        def create_node(data_, parent=None):
            if isinstance(data_, dict):
                name = data_.get('name', 'root')
                data_object = clazz(**data_) if clazz != str else name
                node = Node(name, parent=parent, data=data_object)
                for child_data in data_.get('children', []):
                    create_node(child_data, parent=node)
            else:
                node = Node(str(data_), parent=parent)
            return node

        tree = create_node(data)
        return tree

    @staticmethod
    def from_bean(obj: Any) -> Optional[str]:
        if obj is None:
            return None
        if isinstance(obj, (int, float, Decimal, bool, str)):
            return json.dumps(obj)
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, list):
            return JsonParser.from_list(obj)
        elif isinstance(obj, dict):
            return JsonParser.from_map(obj)
        else:
            return json.dumps(obj, default=lambda o: o.__dict__)

    @staticmethod
    def from_list(obj: List[Any]) -> str:
        if not obj:
            return "[]"
        return json.dumps(obj, default=lambda o: o.__dict__)

    @staticmethod
    def from_map(obj: Dict[Any, Any]) -> str:
        if not obj:
            return "{}"
        return json.dumps(obj, default=lambda o: o.__dict__)

    @staticmethod
    def to_json_by_type(obj: Any, obj_type: Type) -> Optional[str]:
        if obj is None:
            return None
        return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, indent=4)
