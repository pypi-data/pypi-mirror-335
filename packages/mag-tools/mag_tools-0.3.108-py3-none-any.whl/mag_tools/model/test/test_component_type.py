from mag_tools.model.base_enum import BaseEnum


class TestComponentType(BaseEnum):
    """
    测试组件类型枚举
    枚举值为测试组件的名称，如：TestComponentType.TEST_PLAN
    """
    PLAN = ('Plan', '测试计划')  # 测试计划
    MODULE = ('Module', '测试功能模块')  # 测试功能模块
    CASE = ('Case', '测试用例')  # 测试用例
    FUNCTION = ('Function', '测试功能')  # 测试功能
    STEP = ('Step', '测试步骤')  # 测试步骤
