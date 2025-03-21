from mag_tools.model.base_enum import BaseEnum


class ActionType(BaseEnum):
    CLICK = ("click", "单击")
    DOUBLE_CLICK = ("double_click", "双击")
    RIGHT_CLICK = ("right_click", "右键单击")
    CLEAR = ("clear", "清除")
    SUBMIT = ("submit", "提交")
    SEND_KEYS = ("send_keys", "发送按键")
    NONE = ("none", "无操作")
