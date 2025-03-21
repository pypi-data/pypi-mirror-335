import unittest

from mag_tools.format.text_formatter import TextFormatter

from mag_tools.model.justify_type import JustifyType


class TestTextFormat(unittest.TestCase):
    def setUp(self):
        self.format = TextFormatter(
            number_per_line=3,
            justify_type=JustifyType.LEFT,
            at_header='   ',
            decimal_places=3,
            decimal_places_of_zero=3,
            pad_length=None,
            pad_char=' ',
            scientific=False
        )

    def test_to_text(self):
        values = [12.345, 12, 'home', -1232.0000, 123456789010, 1.12e-9, 1.23e5]
        print(f"\n{'\n'.join(self.format.to_lines(values))}")

    def test_to_block(self):
        values = [[12.345, 12, 'home', -1232.0000, 123456789010, 1.12e-9, 1.23e5],
                  [12345.67, 16, 'World', 1232.120, 12345, 1.22e-6, 1.20e3],
                  [122321.345000, 19, 'Earth', 32.02, 6789010, 1.12e3, 2.23e2]]
        print(f"\n{'\n'.join(self.format.to_blocks(values))}")

    def test_array_1d_to_lines(self):
        text_format = TextFormatter(number_per_line=3, justify_type=JustifyType.LEFT)

        # 测试整数数组
        array_1d = [1, 1, 2, 3, 3, 3]
        expected_output = ['2*1 2   3*3']
        result = text_format.array_1d_to_lines(array_1d)
        self.assertEqual(result, expected_output)

        # 测试浮点数数组
        array_1d = [1.1, 1.1, 2.2, 3.3, 3.3, 3.3]
        expected_output = ['2*1.1 2.2   3*3.3']
        result = text_format.array_1d_to_lines(array_1d)
        self.assertEqual(result, expected_output)

        # 测试布尔值数组
        array_1d = [True, True, False, True, True, True]
        expected_output = ['2*True False  3*True']
        result = text_format.array_1d_to_lines(array_1d)
        self.assertEqual(result, expected_output)

        # 测试字符串数组
        array_1d = ['a', 'a', 'b', 'c', 'c', 'c']
        expected_output = ['2*a b   3*c']
        result = text_format.array_1d_to_lines(array_1d)
        self.assertEqual(result, expected_output)

    def test_array_2d_to_lines(self):
        text_format = TextFormatter(number_per_line=3, justify_type=JustifyType.LEFT)

        # 测试整数数组
        array_2d = [
            [1, 1, 2],
            [3, 3, 3]
        ]
        expected_output = ['2*1 2   3*3']
        result = text_format.array_2d_to_lines(array_2d)
        self.assertEqual(result, expected_output)

        # 测试浮点数数组
        array_2d = [
            [1.1, 1.1, 2.2],
            [3.3, 3.3, 3.3]
        ]
        expected_output = ['2*1.1 2.2   3*3.3']
        result = text_format.array_2d_to_lines(array_2d)
        self.assertEqual(result, expected_output)

        # 测试布尔值数组
        array_2d = [
            [True, True, False],
            [True, True, True]
        ]
        expected_output = ['2*True False  3*True']
        result = text_format.array_2d_to_lines(array_2d)
        self.assertEqual(result, expected_output)

        # 测试字符串数组
        array_2d = [
            ['a', 'a', 'b'],
            ['c', 'c', 'c']
        ]
        expected_output = ['2*a b   3*c']
        result = text_format.array_2d_to_lines(array_2d)
        self.assertEqual(result, expected_output)

    def test_array_3d_to_lines(self):
        text_format = TextFormatter(number_per_line=3, justify_type=JustifyType.LEFT)

        # 测试整数数组
        array_3d = [
            [
                [1, 1, 2],
                [3, 3, 3]
            ],
            [
                [4, 4, 5],
                [6, 6, 6]
            ]
        ]
        expected_output = ['2*1 2   3*3', '2*4 5   3*6']
        result = text_format.array_3d_to_lines(array_3d)
        self.assertEqual(expected_output, result)

        # 测试浮点数数组
        array_3d = [
            [
                [1.1, 1.1, 2.2],
                [3.3, 3.3, 3.3]
            ],
            [
                [4.4, 4.4, 5.5],
                [6.6, 6.6, 6.6]
            ]
        ]
        expected_output = ['2*1.1 2.2   3*3.3', '2*4.4 5.5   3*6.6']
        result = text_format.array_3d_to_lines(array_3d)
        self.assertEqual(expected_output, result)

        # 测试布尔值数组
        array_3d = [
            [
                [True, True, False],
                [True, True, True]
            ],
            [
                [False, False, True],
                [False, False, False]
            ]
        ]
        expected_output = ['2*True  False   3*True ', '2*False True    3*False']
        result = text_format.array_3d_to_lines(array_3d)
        self.assertEqual(expected_output, result)

        # 测试字符串数组
        array_3d = [
            [
                ['a', 'a', 'b'],
                ['c', 'c', 'c']
            ],
            [
                ['d', 'd', 'e'],
                ['f', 'f', 'f']
            ]
        ]
        expected_output = ['2*a b   3*c', '2*d e   3*f']
        result = text_format.array_3d_to_lines(array_3d)
        self.assertEqual(expected_output, result)