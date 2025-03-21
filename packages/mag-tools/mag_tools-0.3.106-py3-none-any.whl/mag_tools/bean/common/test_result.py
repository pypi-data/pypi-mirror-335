from typing import Optional


class TestResult:
    def __init__(self, success:Optional[bool]=True, message:Optional[str]=None):
        self.__success = success
        self.__message = message

    def __str__(self):
        return '测试成功' if self.__success else f'测试失败：{self.__message}'

    @classmethod
    def fail(cls, message:str):
        return TestResult(success=False, message=message)