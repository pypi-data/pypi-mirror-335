import re
from typing import List, Optional

import unicodedata

from mag_tools.model.data_type import DataType


class StringUtils:
    @staticmethod
    def pick_head(s: str, keyword: str) -> Optional[str]:
        return s.split(keyword)[0] if s else None

    @staticmethod
    def pick_tail(s: str, keyword: str) -> Optional[str]:
        if s is None or keyword not in s:
            return None

        return s.split(keyword, 1)[1]

    @staticmethod
    def split_by_keyword(input_string: str, keyword: str = '{}'):
        result = None, None, None
        if input_string:
            first, end = keyword[0], keyword[1]
            if first not in input_string or end not in input_string:
                return input_string, None, None
            else:
                pattern = rf'^(.*?)(\{first}(.*?)\{end})(.*)$'
                match = re.match(pattern, input_string)
                if match:
                    result1 = match.group(1) if match.group(1) else None # 第一个捕获组
                    result2 = match.group(3) if match.group(3) else None  # 第三个捕获组
                    result3 = match.group(4) if match.group(4) else None  # 第四个捕获组
                    result = result1, result2, result3
                else:
                    raise ValueError("输入字符串格式不正确")
        return result

    @staticmethod
    def split_name_id(text: str) -> {str, str}:
        """
        将 名称(标识)字符串分为{名称, 标识}
        :param text: 名称(标识)字符串
        :return: {名称, 标识}
        """
        match = re.match(r"(.+)[(（](.+)[)）]", text)
        if match:
            _name = match.group(1)
            _id = match.group(2)
            return _name, _id
        else:
            return text, None

    @staticmethod
    def parse_function(function_name: str) -> tuple:
        """
        解析字符串，将其分解为方法名和参数
        :param function_name: 字符串，格式如：test(arg1, arg2)
        :return: 方法名和参数列表
        """
        pattern = r'(\w+)\((.*)\)'
        match = re.match(pattern, function_name)

        if not match:
            raise ValueError("字符串格式不正确")

        method_name = match.group(1)
        args = match.group(2).split(',') if match.group(2) else []

        # 去除参数两端的空格
        args = [arg.strip() for arg in args]

        return method_name, args

    @staticmethod
    def to_chinese_number(num: int) -> str:
        units = ["", "十", "百", "千", "万", "十", "百", "千", "亿"]
        digits = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]

        if num == 0:
            return "零"

        result = ""
        unit_position = 0
        while num > 0:
            digit = num % 10
            if digit != 0:
                result = f"{digits[digit]}{units[unit_position]}{result}"
            elif result and result[0] != "零":
                result = "零" + result
            num //= 10
            unit_position += 1

        # 处理 "一十" 的情况
        if result.startswith("一十"):
            result = result[1:]

        return result

    @staticmethod
    def parse_strings_to_map(strs: List[str], delimiter: str = ' ') -> dict[str, str]:
        """
        将字符串数组解析为字典。

        参数：
        :param strs: 字符串数组
        :param delimiter: 分隔符，默认为空格
        :return: 字典
        """
        data_map = {}
        for _str in strs:
            if delimiter in _str:
                key, value = _str.split(delimiter, maxsplit=1)
                data_map[key] = value
            else:
                raise ValueError(f"字符串 '{_str}' 中没有分隔符 '{delimiter}'，无法解析为键值对")
        return data_map

    @staticmethod
    def to_value(text: str, data_type: Optional[DataType] = None):
        """
        将文本转换为数值
        :param text: 文本
        :param data_type: 数据类型
        """
        if data_type is None:
            data_type = DataType.get_type(text)

        if data_type == DataType.INTEGER:
            return int(text)
        elif data_type == DataType.FLOAT:
            return float(text)
        elif data_type == DataType.BOOLEAN:
            text = text.lower()
            return text in ['true', 'yes', 't', 'y', '1']
        elif data_type == DataType.LIST:
            return eval(text)
        elif data_type == DataType.DICTIONARY:
            return eval(text)
        else:
            return text

    @staticmethod
    def get_print_width(s: str, chines_width: float = 1.67) -> int:
        width = 0
        for char in s:
            if unicodedata.east_asian_width(char) in ('F', 'W'):
                width += chines_width
            else:
                width += 1
        return int(width)

    @staticmethod
    def remove_between_keywords(text: str, keyword_begin: str, keyword_end: str) -> str:
        # 使用正则表达式去除keyword_begin和keyword_end之间的内容，包括这两个关键词
        pattern = re.escape(keyword_begin) + '.*?' + re.escape(keyword_end)
        return re.sub(pattern, '', text, flags=re.DOTALL)

    @staticmethod
    def float_to_scientific(value: float, decimal_places: int = 6) -> str:
        """
        将 float 数字转换为科学计数法表示的字符串。

        参数：
        :param value: float 数字
        :param decimal_places: 小数位数，默认为 6
        :return: 科学计数法表示的字符串
        """
        exponent = int(f"{value:e}".split('e')[1])
        coefficient = f"{value / (10 ** exponent):.{decimal_places}f}".rstrip('0').rstrip('.')
        if '.' in coefficient:
            integer_part, decimal_part = coefficient.split('.')
            if len(decimal_part) < decimal_places:
                decimal_part += '0' * (decimal_places - len(decimal_part))
            coefficient = f"{integer_part}.{decimal_part}"
        else:
            coefficient += '.' + '0' * decimal_places
        return f"{coefficient}e{exponent}"

    @staticmethod
    def underline2hump(string: str) -> str:
        """
        将用"_"拼接的字符串转换为驼峰格式，首字母小写。

        :param string: String 参数
        """
        # 首字母小写
        string = StringUtils.lower_first_letter(string)
        return re.sub(r'_([a-z])', lambda x: x.group(1).upper(), string)

    @staticmethod
    def hump2underline(s: str) -> str:
        """
        将驼峰格式参数变换为"_"连接的格式。
        """
        s = StringUtils.lower_first_letter(s)
        hump_pattern = re.compile(r'([A-Z])')
        return hump_pattern.sub(r'_\1', s).lower()

    @staticmethod
    def lower_first_letter(string: str) -> str:
        """
        将字符串的首字母转换为小写

        :param string: 输入字符串
        :return: 首字母小写的字符串
        """
        return string[0].lower() + string[1:] if string else ""

    @staticmethod
    def upper_first_letter(string: str) -> str:
        """
        将字符串的首字母转换为小写

        :param string: 输入字符串
        :return: 首字母小写的字符串
        """
        return string[0].upper() + string[1:] if string else ""

    @staticmethod
    def last_word(s: str) -> str:
        """
        获取字段串末尾的关键词，空格分隔

        :param s: 原字符串
        :return: 末尾的关键词
        """
        tokens = s.split()
        return tokens[-1] if tokens else ""

if __name__ == '__main__':
    # 示例使用
    _s = "获取 字段串 末尾的 关键词"
    print(StringUtils.pick_tail(_s, ' '))  # 输出: 关键词

