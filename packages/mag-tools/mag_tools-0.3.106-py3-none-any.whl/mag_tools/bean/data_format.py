from dataclasses import dataclass, field
from typing import Optional

from mag_tools.model.justify_type import JustifyType

@dataclass
class DataFormat:
    justify_type: JustifyType = field(default=JustifyType.LEFT, metadata={'description': '数据对齐方式'})
    decimal_places: int = field(default=2, metadata={'description': '小数位数'})
    decimal_places_of_zero: int = field(default=1, metadata={'description': '小数为0时的小数位数'})
    pad_length: Optional[int] = field(default=None, metadata={'description': '填充长度'})
    scientific: bool = field(default=False, metadata={'description': '是否科学计数法'})

    def __str__(self):
        """
        返回 DataFormat 实例的字符串表示。
        :return: DataFormat 实例的字符串表示。
        """
        return f"DataFormat({', '.join(f'{key}={value}' for key, value in vars(self).items())})"