from typing import Any, Optional, Tuple, Type


class ClassUtils:
    @staticmethod
    def isinstance(bean: Any, cls_types: Tuple[Type, ...]) -> bool:
        return any(isinstance(bean, cls_type) for cls_type in cls_types)

    @staticmethod
    def get_field_type(bean: Any, field_name: str) -> Optional[Type]:
        """
        根据对象和字段名获取字段的类型

        :param bean: 对象
        :param field_name: 字段名
        :return: 字段的类型
        """
        # 获取对象的类型注解
        annotations = getattr(bean, '__annotations__', {})

        # 如果字段在类型注解中，返回类型注解
        if field_name in annotations:
            return annotations[field_name]

        # 否则，尝试获取实例变量的类型
        return type(getattr(bean, field_name, None))


# 示例使用
class MyClass:
    def __init__(self, name, age):
        self.name = name
        self.age = age

if __name__ == '__main__':
    obj = MyClass("Alice", 30)
    field_type = ClassUtils.get_field_type(obj, 'name')
    print(field_type)  # 输出: <class 'str'>

    field_type = ClassUtils.get_field_type(obj, 'age')
    print(field_type)  # 输出: <class 'int'>

    field_type = ClassUtils.get_field_type(obj, 'name')
    print(field_type)  # 输出: <class 'str'>

    field_type = ClassUtils.get_field_type(obj, 'non_existent_field')
    print(field_type)  # 输出: <class 'NoneType'>
