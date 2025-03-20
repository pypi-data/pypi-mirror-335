import random
from datetime import date, datetime
from typing import List, Optional

from mag_tools.bean.data_format import DataFormat
from mag_tools.model.data_type import DataType
from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.common.random_generator import RandomGenerator
from mag_tools.utils.common.string_utils import StringUtils


class StringFormat:
    @staticmethod
    def pad_value(value: str or int or float, pad_length: int, justify_type: JustifyType = JustifyType.RIGHT) -> str:
        """
        将字符串用空格补充到指定长度，空格添加在字符串前。
        参数：
        :param justify_type: 对齐方式，空格补齐
        :param value: 原始数值或字符串
        :param pad_length: 目标长度
        :return: 补充空格后的字符串
        """
        string = str(value)

        if len(string) >= pad_length:
            pad_length = len(string)

        padding_length = pad_length - len(string)
        if justify_type == JustifyType.RIGHT:
            return ' ' * padding_length + string
        elif justify_type == JustifyType.CENTER:
            left_padding = padding_length // 2
            right_padding = padding_length - left_padding
            return ' ' * left_padding + string + ' ' * right_padding
        else:
            return string + ' ' * padding_length

    @staticmethod
    def pad_values(values: List[str or int or float], pad_length: int, justify_type: JustifyType = JustifyType.RIGHT,
                   delimiter: Optional[str] = None) -> str:
        max_length = max(len(str(value)) for value in values)
        pad_length = max(max_length, pad_length)

        if delimiter is None:
            delimiter = ''

        strings = [StringFormat.pad_value(str(value) + delimiter, pad_length, justify_type) for value in values]
        return (' ' if max_length == pad_length else '').join(strings)

    @staticmethod
    def format_number(value: int or float, data_format: Optional[DataFormat] = None) -> str:
        data_type = DataType.get_type(value)
        if data_format is None:
            data_format = DataFormat()

        if data_type not in {DataType.INTEGER, DataType.FLOAT}:
            return value

        if abs(value) >= 1e8 or (value != 0 and abs(value) < 1e-3):
            data_format.scientific = True

        if data_format.scientific:
            return StringUtils.float_to_scientific(value, data_format.decimal_places)

        if data_type == DataType.FLOAT:
            if value.is_integer():
                return f"{value:.{data_format.decimal_places_of_zero}f}"
            else:
                formatted_value = f"{value:.{data_format.decimal_places}f}"
                # 确保小数位末尾的零的个数符合要求
                if '.' in formatted_value:
                    integer_part, decimal_part = formatted_value.split('.')
                    decimal_part = decimal_part.rstrip('0')
                    if len(decimal_part) < data_format.decimal_places_of_zero:
                        decimal_part += '0' * (data_format.decimal_places_of_zero - len(decimal_part))
                    formatted_value = f"{integer_part}.{decimal_part}"
                return formatted_value
        elif data_type == DataType.INTEGER:
            return f"{round(value)}"

    @staticmethod
    def format(template: Optional[str]) -> Optional[str]:
        """
        格式化字符串，处理{}中的特定函数，如果不是函数，则直接返回
        """
        if template is None or not all(c in template for c in '()'):
            return template

        while '{' in template and '}' in template:
            start = template.index('{')
            end = template.index('}', start)
            expression = template[start + 1:end]

            # 解析函数名和参数
            func_name, args = StringUtils.parse_function(expression)

            # 调用相应的函数
            if func_name == 'random_text':
                result = RandomGenerator.ascii_letters(int(args[0]))
            elif func_name == 'random_string':
                result = RandomGenerator.string(int(args[0]))
            elif func_name == 'random_chinese':
                length = int(args[0]) if args[0] else random.randint(1, 100)
                result = RandomGenerator.chinese_string(length)
            elif func_name == 'random_number':
                result = RandomGenerator.number_string(int(args[0]))
            elif func_name == 'random_int':
                min_value = int(args[0] if len(args) >= 2 else 1)
                max_value = int(args[1] if len(args) >= 2 else args[0])

                result = str(random.randint(min_value, max_value))
            elif func_name == 'random_date':
                year = int(args[0]) if len(args) > 0 else date.today().year
                fmt = args[1] if len(args) > 1 else "%Y%m%d"
                result = RandomGenerator.date(year).strftime(fmt)
            elif func_name == 'today':
                fmt = args[0] if len(args) > 0 else "%Y%m%d"
                result = date.today().strftime(fmt)
            elif func_name == 'current':
                fmt = args[0] if len(args) > 0 else "%Y-%m-%d %H:%M:%S"
                result = datetime.now().strftime(fmt)
            else:
                raise ValueError(f"未知的函数: {func_name}")

            # 替换模板中的表达式
            template = template[:start] + result + template[end + 1:]

        return template
