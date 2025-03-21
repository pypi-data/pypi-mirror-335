from appium import webdriver
from appium.webdriver import WebElement
from selenium.webdriver import ActionChains


class EventUtils:
    @staticmethod
    def click(driver:webdriver.Remote, element:WebElement, offset:tuple[int,int]=None):
        if offset:
            offset_x, offset_y = offset
            actions = ActionChains(driver)
            actions.move_to_element_with_offset(element, offset_x, offset_y).click().perform()
        else:
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()