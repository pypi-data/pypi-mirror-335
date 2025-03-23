from typing import Optional
import allure

from mag_tools.bean.common.test_result import TestResult
from mag_tools.utils.common.string_utils import StringUtils

from mag_tools.model.common.log_type import LogType

from mag_tools.log.logger import Logger
from mag_tools.model.test.test_component_type import TestComponentType


class BaseTest:
    def __init__(self, name:str, index:Optional[int]=None, test_component_type:Optional[TestComponentType] = None, description:Optional[str]=None):
        self._name = name
        self._index = index
        self._test_component_type = test_component_type
        self._description = description
        self._test_result = TestResult()

    def _report(self):
        Logger.info(LogType.FRAME, f"执行{self._test_component_type.desc}({self._name})完毕")

        if self._test_component_type == TestComponentType.MODULE:
            index_ch = StringUtils.to_chinese_number(self._index) + "、" if self._index else ""
            allure.dynamic.feature(f"{index_ch}{self._name}")  # 所属功能模块
        elif self._test_component_type == TestComponentType.CASE:
            allure.dynamic.title(self._name)  # 测试用例名（标题）
            if self._description:
                allure.dynamic.story(self._description)  # 测试用例描述
        elif self._test_component_type == TestComponentType.FUNCTION:
            title = self._description if self._description else (self._name if self._name else '')
            allure.step(f"{self._index} {title}  {self._test_result}")  # 描述测试功能
        elif self._test_component_type == TestComponentType.STEP:
            title = self._description if self._description else (self._name if self._name else '')
            allure.step(f"  {self._index} {title}  {self._test_result}")  # 描述测试步骤

    def start(self, driver):
        raise NotImplementedError("This method should be overridden in subclasses")