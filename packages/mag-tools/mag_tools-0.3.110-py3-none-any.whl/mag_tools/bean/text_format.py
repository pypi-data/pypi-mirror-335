from dataclasses import dataclass, field
from typing import Any, List, Optional

import numpy as np

from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.data.value_utils import ValueUtils
from mag_tools.utils.data.string_format import StringFormat


@dataclass
class TextFormat:
    """
    文本拼接的格式，用于将多个字符串拼接为一个文本时使用
    """
    number_per_line: Optional[int] = field(default=None, metadata={"description": "每行显示的数据个数"})
    justify_type: Optional[JustifyType] = field(default=JustifyType.LEFT, metadata={"description": "对齐方式"})
    at_header: Optional[str] = field(default='', metadata={"description": "句首添加的字符串"})
    decimal_places: Optional[int] = field(default=2, metadata={"description": "小数位数"})
    decimal_places_of_zero: Optional[int] = field(default=1, metadata={"description": "小数为0时的小数位数"})
    pad_length: Optional[int] = field(default=None, metadata={"description": "字段显示长度，为 None 表示各字段自行定义"})
    pad_char: Optional[str] = field(default=' ', metadata={"description": "填充占位符"})
    scientific: bool = field(default=False, metadata={"description": "是否使用科学计数法"})

    def __str__(self):
        """
        返回 TextFormat 实例的字符串表示。
        :return: TextFormat 实例的字符串表示。
        """
        return f"TextFormat({', '.join(f'{key}={value}' for key, value in vars(self).items())})"

    def to_lines(self, values: List[Any], max_length: int = None) -> List[str]:
        if max_length is None:
            max_length = self.pad_length

        lines = []
        for value in values:
            if isinstance(value, int) or isinstance(value, float):
                lines.append(ValueUtils.to_string(value, self.decimal_places, self.decimal_places_of_zero, self.scientific))
            else:
                lines.append(str(value))

        return StringFormat.pad_text(lines, max_length, self.justify_type, self.number_per_line, self.at_header)

    def to_blocks(self, values: List[List[Any]]) -> List[str]:
        max_len = max(len(str(item)) for sublist in values for item in sublist)
        lines = []
        for value in values:
            lines.extend(self.to_lines(value, max_len))
        return lines

    def array_1d_to_lines(self, array_1d: List[Any]) -> List[str]:
        """
        将一维数组转换为多行文本表示
        :param array_1d: 一维数组，包含任意类型的数值
        :return: 多行文本表示的数组
        """
        if array_1d is None:
            return []

        result = []
        count = 1
        current_value = array_1d[0]

        max_len = 2
        for i in range(1, len(array_1d)):
            if array_1d[i] == current_value:
                count += 1
            else:
                current_text = ValueUtils.to_string(current_value, self.decimal_places,
                                                    self.decimal_places_of_zero, self.scientific)
                txt = f"{count}*{current_text}" if count > 1 else f"{current_text}"
                max_len = max(max_len, len(txt))
                result.append(txt)

                current_value = array_1d[i]
                count = 1

        # 处理最后一组数据
        current_text = ValueUtils.to_string(current_value, self.decimal_places,
                                            self.decimal_places_of_zero, self.scientific)
        txt = f"{count}*{current_text}" if count > 1 else f"{current_text}"
        max_len = max(max_len, len(txt))
        result.append(txt)

        return self.to_lines(result, max_len)

    def array_2d_to_lines(self, array_2d: List[List[Any]]) -> List[str]:
        """
        生成数值块
        :param array_2d: 二维数组
        :return: 数值块，由多行构成，每行由 "数值" 或 "数值个数*数值"构成
        """

        # 将其展平为一维数组后添加到列表中
        layer = np.array(array_2d).flatten()
        return self.array_1d_to_lines(layer.tolist())

    def array_3d_to_lines(self, array_3d: List[List[List[Any]]]) -> List[str]:
        """
        生成数值块
        :param array_3d: 三维数组
        :return: 数值块，由多行构成，每行由 "数值" 或 "数值个数*数值"构成
        """

        # 遍历每一层并将其展平为一维数组后添加到列表中
        array_1d_sum = []
        num_layers = np.array(array_3d).shape[0]  # 层数
        for i in range(num_layers):
            array_2d = array_3d[i]
            array_1d = np.array(array_2d).flatten()
            array_1d_sum.extend(array_1d.tolist())
            # array_1d_sum.extend(ValueUtils.to_native(value) for value in array_1d)
        return self.array_1d_to_lines(array_1d_sum)
