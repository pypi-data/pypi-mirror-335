from typing import List, Optional

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from mag_tools.model.control_type import ControlType


class ElementFinderUtils:
    @staticmethod
    def local_expression(name:Optional[str], control_type:Optional[ControlType]=None, class_name:Optional[str] = None,
                         automation_id:Optional[str] = None, parent_name:Optional[str]=None,
                         parent_control_type:Optional[ControlType]=None, extended_type:Optional[ControlType]=None):
        exp = ElementFinderUtils.global_expression(name, control_type, class_name, automation_id, parent_name, parent_control_type, extended_type)
        return f".{exp}"

    @staticmethod
    def global_expression(name:Optional[str], control_type:Optional[ControlType]=None, class_name:Optional[str] = None,
                          automation_id:Optional[str] = None, parent_name:Optional[str]=None,
                          parent_control_type:Optional[ControlType]=None, extended_type:Optional[ControlType]=None):
        exp = ""
        if parent_name:
            parent_tag_name = f"{parent_control_type.code}" if parent_control_type is not None else "*"
            exp = f"{exp}//{parent_tag_name}[@Name='{parent_name}']"

        tag_name = f"{control_type.code}" if control_type is not None else "*"
        exp = f"{exp}//{tag_name}"

        name_str = None
        if name:
            name_str = f"@Name='{name}'"
        if class_name:
            name_str = f"{name_str} and @ClassName='{class_name}'" if name_str else f"@ClassName='{class_name}'"
        if automation_id:
            name_str = f"{name_str} and @AutomationId='{automation_id}'" if name_str else f"@AutomationId='{automation_id}'"

        if name_str:
            exp = f"{exp}[{name_str}]"

        if extended_type:
            exp = f"{exp}//{extended_type.code}"

        return exp

    @staticmethod
    def find_element_by_type(element:WebElement, name:Optional[str], control_type:Optional[ControlType]=None, parent_name:Optional[str]=None,
                             parent_control_type:Optional[ControlType]=None, extended_type:Optional[ControlType]=None):
        exp = ElementFinderUtils.local_expression(name, control_type, None, None, parent_name, parent_control_type, extended_type)
        return element.find_element(By.XPATH, exp)

    @staticmethod
    def find_element_by_class(element:WebElement, name:Optional[str], class_name:Optional[str]=None, parent_name:Optional[str]=None,
                              parent_control_type:Optional[ControlType]=None, extended_type:Optional[ControlType]=None):
        exp = ElementFinderUtils.local_expression(name, None, class_name, None, parent_name, parent_control_type, extended_type)
        return element.find_element(By.XPATH, exp)

    @staticmethod
    def find_element_by_automation(element:WebElement, automation_id:str, extended_type:Optional[ControlType]=None):
        exp = ElementFinderUtils.local_expression(None, None, None, automation_id, None, None, extended_type)
        return element.find_element(By.XPATH, exp)

    @staticmethod
    def find_elements_by_type(element:WebElement, name:Optional[str], control_type:Optional[ControlType]=None, parent_name:Optional[str]=None,
                              parent_control_type:Optional[ControlType]=None, extended_type:Optional[ControlType]=None):
        exp = ElementFinderUtils.local_expression(name, control_type, None, None, parent_name, parent_control_type, extended_type)
        return element.find_elements(By.XPATH, exp)

    @staticmethod
    def find_elements_by_class(element:WebElement, name:str, class_name:Optional[str]=None, parent_name:Optional[str]=None,
                               parent_control_type:Optional[ControlType]=None, extended_type:Optional[ControlType]=None):
        exp = ElementFinderUtils.local_expression(name, None, class_name, None, parent_name, parent_control_type, extended_type)
        return element.find_elements(By.XPATH, exp)

    @staticmethod
    def find_element_by_types(element:WebElement, name:str, control_types:List[ControlType], parent_name:Optional[str]=None,
                              parent_control_type:Optional[ControlType]=None, extended_type:Optional[ControlType]=None):
        ele = None
        for control_type in control_types:
            try:
                ele = ElementFinderUtils.find_element_by_type(element, name, control_type, parent_name, parent_control_type, extended_type)
            except NoSuchElementException:
                pass
        return ele