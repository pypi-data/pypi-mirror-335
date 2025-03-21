from build.lib.mag_tools.model.base_enum import BaseEnum


class ProcessResult(BaseEnum):
    SUCCESS = ('success', '成功')
    FAIL = ('fail', '失败')
    UNKNOWN = ('unknown', '未知')