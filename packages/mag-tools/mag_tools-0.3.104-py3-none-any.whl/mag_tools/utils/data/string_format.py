import random
from datetime import date, datetime
from typing import List, Optional

from mag_tools.utils.data.string_utils import StringUtils

from mag_tools.model.justify_type import JustifyType
from mag_tools.utils.data.random_generator import RandomGenerator
from mag_tools.utils.data.list_utils import ListUtils


class StringFormat:
    @staticmethod
    def pad_string(string: str, pad_len: Optional[int] = None, justify: JustifyType = JustifyType.RIGHT) -> str:
        """
        将字符串用空格补充到指定长度，空格添加在字符串前。
        参数：
        :param justify: 对齐方式，空格补齐
        :param string: 原始数值或字符串
        :param pad_len: 目标长度
        :return: 补充空格后的字符串
        """
        pad_len = max(len(string), pad_len) if pad_len is not None else len(string)

        padding_size = pad_len - len(string) #要填充的占位符个数
        if justify == JustifyType.RIGHT:
            return f"{' ' * padding_size}{string}"
        elif justify == JustifyType.CENTER:
            left_padding = ' ' * (padding_size // 2)
            right_padding = ' ' * (padding_size - padding_size // 2)
            return  f'{left_padding}{string}{right_padding}'
        else:
            return f"{string}{' ' * padding_size}"

    @staticmethod
    def pad_text(strings: List[str], pad_len: Optional[int] = None, justify: JustifyType = JustifyType.RIGHT, number_per_line: int = None, at_header: str = None) -> List[str]:
        if number_per_line is None:
            number_per_line = len(strings)
        at_header = at_header if at_header else ''

        max_length = max(len(str(s)) for s in strings)
        pad_len = max(pad_len, max_length) if pad_len is not None else max_length

        items = [StringFormat.pad_string(s, pad_len, justify) for s in strings]
        blocks = ListUtils.split(items, number_per_line)
        lines = [at_header + (' ' if max_length == pad_len else '').join(block) for block in blocks]
        return lines

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

