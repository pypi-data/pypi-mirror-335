from dataclasses import MISSING, dataclass, field, fields
from typing import Any, Dict

from mag_tools.format.text_formatter import TextFormatter
from mag_tools.model.justify_type import JustifyType


@dataclass
class BaseData:
    """
    Bean的基类
    """
    _formatter = TextFormatter(
        number_per_line=None,
        justify_type=JustifyType.LEFT,
        at_header='',
        at_end='',
        decimal_places=6,
        decimal_places_of_zero=2,
        pad_length=None,
        pad_char=' ',
        scientific=False,
        none_default='NA'
    )

    def __repr__(self):
        field_dict = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        field_str = ', '.join(f"{k}={v}" for k, v in field_dict.items())
        return f"{self.__class__.__name__}({field_str})"

    def __str__(self):
        excluded_attributes = {}
        attributes = [
            f"{attr}={repr(getattr(self, attr))}"
            for attr in vars(self)
            if getattr(self, attr) is not None and attr not in excluded_attributes
        ]
        return f"{self.__class__.__name__}({', '.join(attributes)})"

    @classmethod
    def get_default_value(cls, field_name: str) -> Any:
        """
        获取字段的缺省值
        """
        for f in fields(cls):   # type: ignore
            if f.name == field_name:
                return f.default if f.default is not MISSING else None
        raise ValueError(f"Field '{field_name}' not found in {cls.__name__}")

    @property
    def to_map(self) -> Dict[str, Any]:
        return {
            k: repr(v) for k, v in self.__dict__.items()
            if not (k.startswith('__') and k.endswith('__')) and k not in {'_text_format', '_data_formats'}
        }

@dataclass
class TestData(BaseData):
    name: str = field(default=None, metadata={"description": "UUID"})
    age: int = field(default=12, metadata={"description": "UUID"})
    height: float = field(default=1.56, metadata={"description": "UUID"})


if __name__ == '__main__':
    data = TestData(name='xlcao', age=12, height=1)
    age_ = TestData.get_default_value('height')
    print(age_)