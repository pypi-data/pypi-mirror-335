from mag_tools.model.base_enum import BaseEnum


class FunctionStatus(BaseEnum):
    NORMAL = (1, "正常")  # 活动状态，可执行
    CLOSED = (0, "关闭")  # 关闭状态
    LOCKED = (9, "停用")  # 暂停使用
