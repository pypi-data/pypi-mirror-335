import unittest

from mag_tools.bean.data_format import DataFormat

from mag_tools.model.data_type import DataType

from mag_tools.utils.data.string_utils import StringUtils
from mag_tools.utils.data.string_format import StringFormat


class TestStringStringUtils(unittest.TestCase):

    def test_get_before_keyword(self):
        self.assertEqual(StringUtils.pick_head("hello world", "world"), "hello ")
        self.assertEqual(StringUtils.pick_head("hello world", " "), "hello")
        self.assertEqual(StringUtils.pick_head("hello world", "hello"), "")

    def test_get_after_keyword(self):
        self.assertEqual(StringUtils.pick_tail("hello world", "hello"), " world")
        self.assertIsNone(StringUtils.pick_tail("hello world", "world"))
        self.assertIsNone(StringUtils.pick_tail("hello world", "notfound"))

    def test_split_by_keyword(self):
        _input_strings = [
            "{打开工区}",
            "打开工区",
            "GridControl{T}",
            "打开工区(AAA)",
            "打开工区[AAA]BBB",
            "打开工区'AAA'BBB",
            '打开工区"AAA"BBB',
        ]

        _keywords = ['{}', '{}', '()', '[]', "''", '""']

        for _input_string, _keyword in zip(_input_strings, _keywords):
            _name, _function, _remainder = StringUtils.split_by_keyword(_input_string, _keyword)
            print(f"Input: {_input_string} -> Name: {_name}, Function: {_function}, Remainder: {_remainder}")

    def test_split_name_id(self):
        self.assertEqual(StringUtils.split_name_id("名称(标识)"), ("名称", "标识"))
        self.assertEqual(StringUtils.split_name_id("名称（标识）"), ("名称", "标识"))
        self.assertEqual(StringUtils.split_name_id("名称标识"), ("名称标识", None))

    def test_parse_function(self):
        self.assertEqual(StringUtils.parse_function("test(arg1, arg2)"), ("test", ["arg1", "arg2"]))
        self.assertEqual(StringUtils.parse_function("test()"), ("test", []))
        with self.assertRaises(ValueError):
            StringUtils.parse_function("test")

    def test_to_chinese_number(self):
        self.assertEqual(StringUtils.to_chinese_number(0), "零")
        self.assertEqual(StringUtils.to_chinese_number(10), "十")
        self.assertEqual(StringUtils.to_chinese_number(110), "一百一十")
        self.assertEqual(StringUtils.to_chinese_number(1234), "一千二百三十四")
        self.assertEqual(StringUtils.to_chinese_number(10001), "一万零一")

    def test_to_value(self):
        # 测试整数转换
        self.assertEqual(StringUtils.to_value("123", int), 123)
        # 测试浮点数转换
        self.assertEqual(StringUtils.to_value("123.45", float), 123.45)
        # 测试布尔值转换
        self.assertTrue(StringUtils.to_value("true", bool))
        self.assertFalse(StringUtils.to_value("false", bool))
        # 测试列表转换
        self.assertEqual(StringUtils.to_value("[1, 2, 3]", list), [1, 2, 3])
        # 测试字典转换
        self.assertEqual(StringUtils.to_value("{'key': 'value'}", dict), {'key': 'value'})
        # 测试默认类型转换
        self.assertEqual(StringUtils.to_value("text"), "text")

    def test_format_value(self):
        # 测试浮点数格式化
        data_format = DataFormat(decimal_places_of_zero=2)
        self.assertEqual(StringFormat.format_number(123.456, data_format), "123.46")
        self.assertEqual(StringFormat.format_number(123.0, data_format), "123.00")
        # 测试科学计数法格式化
        self.assertEqual(StringFormat.format_number(1e9, DataFormat(decimal_places=6, scientific=True)), "1.000000e9")
        # 测试整数格式化
        self.assertEqual(StringFormat.format_number(123, DataFormat()), "123")

    def test_float_to_scientific(self):
        # 测试默认小数位数
        self.assertEqual(StringUtils.float_to_scientific(1000000000.0), "1.000000e9")
        self.assertEqual(StringUtils.float_to_scientific(0.000123), "1.230000e-4")

        # 测试指定小数位数
        self.assertEqual(StringUtils.float_to_scientific(1000000000.0, 5), "1.00000e9")
        self.assertEqual(StringUtils.float_to_scientific(0.000123, 3), "1.230e-4")

        # 测试负数
        self.assertEqual(StringUtils.float_to_scientific(-1000000000.0), "-1.000000e9")
        self.assertEqual(StringUtils.float_to_scientific(-0.000123), "-1.230000e-4")

        # 测试小数位数不足时补零
        self.assertEqual(StringUtils.float_to_scientific(1.23, 5), "1.23000e0")
        self.assertEqual(StringUtils.float_to_scientific(1.0, 5), "1.00000e0")

    def test_parse_strings_to_map(self):
        # 测试用例 1：使用空格作为分隔符
        strs = [
            "key1 value1",
            "key2 value2",
            "key3 value3"
        ]
        expected_output = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        result = StringUtils.parse_strings_to_map(strs)
        self.assertEqual(result, expected_output)

        # 测试用例 2：使用逗号作为分隔符
        strs = [
            "key1,value1",
            "key2,value2",
            "key3,value3"
        ]
        expected_output = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        result = StringUtils.parse_strings_to_map(strs, delimiter=',')
        self.assertEqual(result, expected_output)

        # 测试用例 3：字符串中没有分隔符
        strs = [
            "key1 value1",
            "key2value2",  # 没有空格
            "key3 value3"
        ]
        with self.assertRaises(ValueError):
            StringUtils.parse_strings_to_map(strs)

        # 测试用例 4：字符串中有多个分隔符
        strs = [
            "key1 value1",
            "key2  value2",  # 多个空格
            "key3 value3"
        ]
        expected_output = {
            "key1": "value1",
            "key2": " value2",
            "key3": "value3"
        }
        result = StringUtils.parse_strings_to_map(strs)
        self.assertEqual(result, expected_output)

    def test_underline2hump(self):
        self.assertEqual(StringUtils.underline2hump('family_address'), 'familyAddress')
        self.assertEqual(StringUtils.underline2hump('my_variable_name'), 'myVariableName')
        self.assertEqual(StringUtils.underline2hump('test_case'), 'testCase')
        self.assertEqual(StringUtils.underline2hump('example_string'), 'exampleString')

    def test_hump2underline(self):
        self.assertEqual(StringUtils.hump2underline('familyAddress'), 'family_address')
        self.assertEqual(StringUtils.hump2underline('myVariableName'), 'my_variable_name')
        self.assertEqual(StringUtils.hump2underline('testCase'), 'test_case')
        self.assertEqual(StringUtils.hump2underline('exampleString'), 'example_string')

if __name__ == '__main__':
    unittest.main()
