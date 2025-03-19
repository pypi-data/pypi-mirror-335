from mag_tools.utils.common.string_utils import StringUtils
from mag_tools.model.base_enum import BaseEnum


class ControlType(BaseEnum):
    """
    控件类型枚举
    枚举值为不包含前缀的控件类型名，如：ControlType.EDIT
    """

    EDIT = ('Edit', '文本框')  # TextBox
    DOC = ('Document', '文档')  # Document
    BUTTON = ('Button', '按钮')  # Button
    SPLIT_BUTTON = ('SplitButton', '拆分按钮')  # SplitButton
    CHECKBOX = ('CheckBox', '复选框')  # CheckBox
    RADIO = ('RadioButton', '单选按钮')  # RadioButton
    MENU_BAR = ('MenuBar', '菜单栏')  # MenuBar
    MENU = ('Menu', '菜单')  # Menu
    MENU_ITEM = ('MenuItem', '菜单项')  # MenuItem
    CONTEXT_MENU = ('ContextMenu', '上下文菜单')  # ContextMenu
    WINDOW = ('Window', '主窗口')  # Main Window
    DIALOG = ('Dialog', '对话框')  # Dialog
    MESSAGE = ('MessageBox', '消息框')  # MessageBox
    LABEL = ('Text', '标签')  # Label
    LIST = ('List', '列表框')  # ListBox
    LIST_VIEW = ('ListView', '列表视图')  # ListView
    LIST_ITEM = ('ListItem', '列表项')  # ListBox/ListView包含ListItem
    COMBO_BOX = ('ComboBox', '组合框')  # ComboBox
    TREE = ('Tree', '树视图')  # TreeView
    TREE_ITEM = ('TreeItem', '树节点')  # TreeItem
    TAB = ('Tab', '选项卡')  # TabControl
    TAB_ITEM = ('TabItem', 'Tab项')  # Tab项
    GROUP_TAB = ('GroupTab', '组TabItem')  # 组TabItem
    DATETIME = ('SysDateTimePick32', '日期时间')  # 类名为 SysDateTimePick32
    PROGRESS = ('ProgressBar', '进度条')  # ProgressBar
    TITLE = ('TitleBar', '标题栏')  # TitleBar
    SLIDER = ('Slider', '滑块')  # Slider
    STATUS = ('StatusBar', '状态条')  # StatusBar
    TOOL = ('ToolBar', '工具栏')  # ToolBar
    GROUP = ('Group', '组')  # 组Group
    PANEL = ('Panel', 'Panel')  # Panel 分组和布局
    PANE = ('Pane', 'Pane')  # Panel 分组框或面板

    @classmethod
    def get_by_element(cls, element):
        if element is None:
            return None

        type_name = StringUtils.get_after_keyword(element.tag_name, ".")
        return ControlType.get_by_code(type_name)

    def is_composite(self):
        return self in {ControlType.BUTTON, ControlType.SPLIT_BUTTON, ControlType.MENU, ControlType.COMBO_BOX,
                        ControlType.LIST, ControlType.LIST_VIEW, ControlType.TREE, ControlType.PANE,
                        ControlType.TOOL, ControlType.DATETIME, ControlType.WINDOW}
