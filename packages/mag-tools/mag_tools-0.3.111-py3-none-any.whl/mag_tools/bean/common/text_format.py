from typing import Optional, Any

from mag_tools.bean.common.data_format import DataFormat
from mag_tools.model.common.justify_type import JustifyType


class TextFormat(DataFormat):
    def __init__(self, number_per_line: Optional[int] = 1, justify_type: Optional[JustifyType] = JustifyType.LEFT,
                 at_header: Optional[str] = '', decimal_places: Optional[int] = 2,
                 decimal_places_of_zero: Optional[int] = 1, pad_length: Optional[int] = None, scientific: bool = False):
        """
        数据格式
        :param number_per_line: 每行显示的数据个数
        :param justify_type: 对齐方式
        :param at_header: 句首添加的字符串
        :param decimal_places: 小数位数
        :param pad_length: 字段显示长度，为 None 表示各字段自行定义
        :param decimal_places_of_zero: 小数为0时的小数位数
        """
        super().__init__(justify_type, decimal_places, decimal_places_of_zero, pad_length, scientific)

        self.number_per_line = number_per_line
        self.at_header = at_header
        self.scientific = scientific

    def __str__(self):
        """
        返回 TextFormat 实例的字符串表示。
        :return: TextFormat 实例的字符串表示。 """
        return f"TextFormat({', '.join(f'{key}={value}' for key, value in vars(self).items())})"

    def get_data_format(self, pad_length: int) -> DataFormat:
        return DataFormat(self.justify_type, self.decimal_places, self.decimal_places_of_zero, pad_length,
                          self.scientific)

    def get_data_format_by_value(self, value: Any):
        return self.get_data_format(len(str(value)))
