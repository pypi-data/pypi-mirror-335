from mag_tools.model.justify_type import JustifyType

from mag_tools.bean.data_format import DataFormat
from mag_tools.utils.data.string_format import StringFormat
import unittest


class TestStringFormat(unittest.TestCase):
    def test_pad_string(self):
        # 测试右对齐
        self.assertEqual(StringFormat.pad_value("test", 10), "      test")
        # 测试居中对齐
        self.assertEqual(StringFormat.pad_value("test", 10, JustifyType.CENTER), "   test   ")
        # 测试左对齐
        self.assertEqual(StringFormat.pad_value("test", 10, JustifyType.LEFT), "test      ")
        # 测试字符串长度大于目标长度
        self.assertEqual(StringFormat.pad_value("test", 2), "test")

    def test_pad_strings(self):
        # 测试多个字符串右对齐
        strings = ["test1", "test2", "test3"]
        expected_output = "     test1     test2     test3"
        self.assertEqual(expected_output, StringFormat.pad_values(strings, 10))
        # 测试多个字符串居中对齐
        expected_output = " test1   test2   test3  "
        self.assertEqual(expected_output, StringFormat.pad_values(strings, 8, JustifyType.CENTER))
        # 测试多个字符串左对齐
        expected_output = "test1 test2 test3"
        self.assertEqual(expected_output, StringFormat.pad_values(strings, 5, JustifyType.LEFT))

    def test_format_number(self):
        # 测试整数格式化
        data_format = DataFormat()
        self.assertEqual("123", StringFormat.format_number(123, data_format))

        # 测试浮点数格式化
        data_format = DataFormat(decimal_places_of_zero=2)
        self.assertEqual("123.46", StringFormat.format_number(123.456, data_format))
        self.assertEqual("123.00", StringFormat.format_number(123.0, data_format))

        # 测试科学计数法格式化
        data_format = DataFormat(decimal_places=5, scientific=True)
        self.assertEqual(StringFormat.format_number(1e9, data_format), "1.00000e9")
        self.assertEqual(StringFormat.format_number(1e-4, data_format), "1.00000e-4")

        # 测试非数值类型
        self.assertEqual(StringFormat.format_number("text", data_format), "text")

    def test_format(self):
        print(StringFormat.format("{random_text(5)}"))
        print(StringFormat.format("{random_string(3)}"))
        print(StringFormat.format("{random_chinese(12)}"))
        print(StringFormat.format("{random_number(4)}"))
        print(StringFormat.format("{random_date(2024,%Y-%m-%d)}"))
        print(StringFormat.format("{today(%Y%m%d)}"))
        print(StringFormat.format("{current(%Y-%m-%d %H:%M:%S)}"))
        print(StringFormat.format("{random_int(20, 30)}"))


if __name__ == '__main__':
    unittest.main()
