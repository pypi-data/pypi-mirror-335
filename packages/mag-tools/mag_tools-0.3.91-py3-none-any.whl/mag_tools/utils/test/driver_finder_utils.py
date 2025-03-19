
from typing import Optional

from appium import webdriver

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from mag_tools.model.control_type import ControlType
from mag_tools.utils.test.element_finder_utils import ElementFinderUtils


class DriverFinderUtils:
    @staticmethod
    def find_element_by_type(driver: webdriver.Remote, name: Optional[str], control_type: Optional[ControlType] = None, parent_name: Optional[str] = None, parent_control_type: Optional[ControlType] = None):
        if name:
            exp = ElementFinderUtils.global_expression(name, control_type, None, None, parent_name, parent_control_type)
            return driver.find_element(By.XPATH, exp)
        else:
            elements = DriverFinderUtils.find_elements_by_type(driver, None, control_type, parent_name, parent_control_type)
            for element in elements:
                if element.get_attribute("Name") is None:
                    return element

    @staticmethod
    def find_element_by_class(driver: webdriver.Remote, name: Optional[str], class_name: Optional[str] = None, parent_name: Optional[str] = None, parent_control_type: Optional[ControlType] = None):
        if name:
            exp = ElementFinderUtils.global_expression(name, None, class_name, None, parent_name, parent_control_type)
            return driver.find_element(By.XPATH, exp)
        else:
            elements = DriverFinderUtils.find_elements_by_class(driver, None, class_name, parent_name, parent_control_type)
            for element in elements:
                if element.get_attribute("Name") is None:
                    return element

    @staticmethod
    def find_element_by_automation(driver: webdriver.Remote, automation_id: Optional[str]):
        exp = ElementFinderUtils.global_expression(None, None, None, automation_id, None, None)
        return driver.find_element(By.XPATH, exp)

    @staticmethod
    def find_element_by_type_wait(driver: webdriver.Remote, name: Optional[str], control_type: Optional[ControlType] = None, parent_name: Optional[str] = None, parent_control_type: Optional[ControlType] = None):
        if name:
            exp = ElementFinderUtils.global_expression(name, control_type, None, None, parent_name, parent_control_type)
            wait = WebDriverWait(driver, 5)
            return wait.until(EC.presence_of_element_located((By.XPATH, exp)))
        else:
            elements = DriverFinderUtils.find_elements_by_type_wait(driver, None, control_type, parent_name, parent_control_type)
            for element in elements:
                if element.get_attribute("Name") is None:
                    return element

    @staticmethod
    def find_element_by_class_wait(driver: webdriver.Remote, name: Optional[str], class_name: Optional[str] = None, parent_name: Optional[str] = None, parent_control_type: Optional[ControlType] = None):
        if name:
            exp = ElementFinderUtils.global_expression(name, None, class_name, None, parent_name, parent_control_type)
            wait = WebDriverWait(driver, 5)
            return wait.until(EC.presence_of_element_located((By.XPATH, exp)))
        else:
            elements = DriverFinderUtils.find_elements_by_class_wait(driver, None, class_name, parent_name, parent_control_type)
            for element in elements:
                if element.get_attribute("Name") is None:
                    return element

    @staticmethod
    def find_element_by_automation_wait(driver: webdriver.Remote, automation_id: Optional[str]):
        exp = ElementFinderUtils.global_expression(None, None, None, automation_id, None, None)
        wait = WebDriverWait(driver, 5)
        return wait.until(EC.presence_of_element_located((By.XPATH, exp)))

    @staticmethod
    def find_elements_by_type_wait(driver: webdriver.Remote, name: Optional[str], control_type: Optional[ControlType] = None, parent_name: Optional[str] = None, parent_control_type: Optional[ControlType] = None):
        exp = ElementFinderUtils.global_expression(name, control_type, None, None, parent_name, parent_control_type)
        wait = WebDriverWait(driver, 5)
        return wait.until(EC.presence_of_all_elements_located((By.XPATH, exp)))

    @staticmethod
    def find_elements_by_class_wait(driver: webdriver.Remote, name: Optional[str], class_name: Optional[str] = None, parent_name: Optional[str] = None, parent_control_type: Optional[ControlType] = None):
        exp = ElementFinderUtils.global_expression(name, None, class_name, None, parent_name, parent_control_type)
        wait = WebDriverWait(driver, 5)
        return wait.until(EC.presence_of_all_elements_located((By.XPATH, exp)))

    @staticmethod
    def find_elements_by_type(driver: webdriver.Remote, name: Optional[str], control_type: Optional[ControlType] = None, parent_name: Optional[str] = None, parent_control_type: Optional[ControlType] = None):
        exp = ElementFinderUtils.global_expression(name, control_type, None, None, parent_name, parent_control_type)
        return driver.find_elements(By.XPATH, exp)

    @staticmethod
    def find_elements_by_class(driver: webdriver.Remote, name: Optional[str], class_name: Optional[str] = None, parent_name: Optional[str] = None, parent_control_type: Optional[ControlType] = None):
        exp = ElementFinderUtils.global_expression(name, None, class_name, None, parent_name, parent_control_type)
        return driver.find_elements(By.XPATH, exp)

    @staticmethod
    def find_element_by_types(driver: webdriver.Remote, name: Optional[str], control_types: list[ControlType] = None, parent_name: Optional[str] = None, parent_control_type: Optional[ControlType] = None):
        element = None
        for control_type in control_types:
            try:
                element = DriverFinderUtils.find_element_by_type(driver, name, control_type, parent_name, parent_control_type)
                break
            except NoSuchElementException:
                pass
        return element