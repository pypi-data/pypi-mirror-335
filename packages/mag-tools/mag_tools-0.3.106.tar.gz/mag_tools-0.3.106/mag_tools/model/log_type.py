from mag_tools.model.base_enum import BaseEnum


class LogType(BaseEnum):
    ROOT = ('root', '根')
    FRAME = ('frame', '框架')
    DAO = ('dao', '数据库')
    SERVICE = ('service', '服务')
    PERFORMANCE = ('performance', '性能')
