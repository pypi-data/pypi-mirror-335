from typing import Optional, List

from mag_tools.bean.common.data_format import DataFormat
from mag_tools.bean.common.text_format import TextFormat
from mag_tools.model.common.justify_type import JustifyType
from mag_tools.utils.common.string_format import StringFormat


class BaseData:
    _text_format: TextFormat
    _data_formats: Optional[dict]

    def __init__(self):
        self._text_format = TextFormat(number_per_line=4, justify_type=JustifyType.LEFT, at_header='',
                                       decimal_places=4,
                                       decimal_places_of_zero=1)
        self._data_formats = None

    def set_pad_lengths(self, pad_lengths: dict[str, int]):
        for arg_name, value in pad_lengths.items():
            data_format = self.get_data_format(arg_name)
            if data_format is None:
                data_format = self._text_format.get_data_format_by_value(vars(self).get(arg_name))
            data_format.pad_length = value

    def set_same_pad_length(self, pad_length:int):
        for data_format in self._data_formats:
            data_format.set_pad_length(pad_length)

    def set_justify_type(self, justify_type: JustifyType):
        self._text_format.justify_type = justify_type
        for data_format in self._data_formats:
            data_format.justify_type = justify_type

    def set_decimal_places(self, decimal_places):
        self._text_format.decimal_places = decimal_places
        for data_format in self._data_formats:
            data_format.decimal_places = decimal_places

    def set_decimal_places_of_zero(self, decimal_places_of_zero):
        self._text_format.decimal_places_of_zero = decimal_places_of_zero
        for data_format in self._data_formats:
            data_format.decimal_places_of_zero = decimal_places_of_zero

    def set_number_per_line(self, number_per_line):
        self._text_format.number_per_line = number_per_line

    def set_at_header(self, at_header):
        self._text_format.at_header = at_header

    def set_scientific(self, scientific):
        self._text_format.scientific = scientific

    def get_text(self, arg_names: List[str], delimiter: Optional[str] = None) -> str:
        """
        根据参数名数组拼成一个字符串。
        :param arg_names: 类成员变量的名字数组
        :param delimiter: 分隔符
        :return: 拼接后的字符串
        """

        if delimiter is None:
            delimiter = ''

        strings = []
        need_space = False
        for arg_name in arg_names:
            data_format = self.get_data_format(arg_name)
            value_str = str(vars(self).get(arg_name))
            pad_length = max(len(value_str), data_format.pad_length)
            need_space = need_space or pad_length == len(value_str)

            strings.append(StringFormat.pad_value(value_str, pad_length, data_format.justify_type))

        text = (' ' if need_space else '').join(strings)
        if delimiter:
            text = text.rstrip(delimiter)  # 删除末尾的分隔符
        return text

    def get_data_format(self, arg_name: str) -> DataFormat:
        if self._data_formats is None:
            self._data_formats = {}
            for name, value in vars(self).items():
                if name not in ['text_format', 'data_formats']:
                    self._data_formats[name] = self._text_format.get_data_format_by_value(value)

        return self._data_formats[arg_name]

class TestData(BaseData):
    def __init__(self, name: Optional[str] = None, age: Optional[int] = None, height: Optional[float] = None):
        super().__init__()

        self.name = name
        self.age = age
        self.height = height


if __name__ == '__main__':
    data = TestData('xlcao', 12, 1)
    print(data.get_text(['name', 'age', 'height'], ','))

    data.set_pad_lengths({'name': 20, 'age': 8, 'height': 10})
    print(data.get_text(['name', 'age', 'height'], ','))

    data.set_justify_type(JustifyType.LEFT)
    print(data.get_text(['name', 'age', 'height'], ','))

    data.set_justify_type(JustifyType.CENTER)
    print(data.get_text(['name', 'age', 'height'], ','))
