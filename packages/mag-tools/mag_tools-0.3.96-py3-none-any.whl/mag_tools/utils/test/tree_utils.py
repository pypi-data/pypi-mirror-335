from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from mag_tools.model.control_type import ControlType
from mag_tools.utils.test.element_finder_utils import ElementFinderUtils


class TreeUtils:
    @staticmethod
    def expand_all(driver:WebDriver, tree:WebElement):
        try:
            # 查找所有展开按钮
            expand_buttons = ElementFinderUtils.find_element_by_type(tree, 'Expand', ControlType.BUTTON)

            for button in expand_buttons:
                # 点击展开按钮
                button.click()
                # 等待子节点加载完成
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, './/Button[@content-desc="Expand"]')))
                # 递归展开子节点
                TreeUtils.expand_all(driver, tree)
        except Exception as e:
            print(f"Error expanding nodes: {str(e)}")