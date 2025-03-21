from mag_tools.model.base_enum import BaseEnum


class DataType(BaseEnum):
    NONE = (0, "无类型")  #: 无类型
    INTEGER = (1, "整数类型")  #: 整数类型
    FLOAT = (2, "浮点数类型")  #: 浮点数类型
    STRING = (3, "字符串类型")  #: 字符串类型
    BOOLEAN = (4, "布尔类型")  #: 布尔类型
    LIST = (5, "列表类型")  #: 列表类型
    DICTIONARY = (6, "字典类型")  #: 字典类型

    @classmethod
    def get_type(cls, value):
        """
        根据值的类型返回对应的 DataType 枚举类型。

        :param value: 要判断类型的值
        :return: 对应的 DataType 枚举类型
        """
        _type = cls.STRING  # 默认类型为 STRING

        if value is None:
            _type = cls.NONE
        elif isinstance(value, bool):
            _type = cls.BOOLEAN
        elif isinstance(value, int):
            _type = cls.INTEGER
        elif isinstance(value, float):
            _type = cls.FLOAT
        elif isinstance(value, str):
            if value.startswith('[') and value.endswith(']'):
                _type = cls.LIST
            elif value.startswith('{') and value.endswith('}'):
                _type = cls.DICTIONARY

        return _type


if __name__ == '__main__':
    # 示例用法
    print(DataType.INTEGER.code)  # 输出: 1
    print(DataType.INTEGER.desc)  # 输出: 整数类型
    print(DataType.of_code(1).desc)  # 输出: 整数类型
    print(DataType.get_type(123))  # 输出: DataType.INTEGER
