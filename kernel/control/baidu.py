import re

from kernel.base_class.base_class import *
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class Baidu(BaseClass):
    __startMain = "https://adminpro.iviewui.com/login"
    __driver = None
    def __init__(self,argv):
        pass

    def main(self,argv):
        self.__driver = self.selenium_mode.open_url(self.__startMain)
        # #driver.implicity_wait(30)
        # #driver.maximize_window()
        #.text
        # browser = webdriver.Firefox()
        #print("driver",self.__driver)
        #user = self.__driver.find_element(By.CSS_SELECTOR, '[name="username"]')
        #print("user",user)
        #user.send_keys("admin")
        #pwd = self.__driver.find_element(By.CSS_SELECTOR, "[name='password']")
        #print("pwd",pwd)
        #pwd.send_keys("admin")
        submit = self.__driver.find_element(By.CSS_SELECTOR, ".ivu-btn.ivu-btn-primary.ivu-btn-long.ivu-btn-large")
        submit.click()
        time.sleep(3)
        menu = self.selenium_mode.find_text_from(".i-layout-menu-side-title-text.i-layout-menu-side-title-text-with-icon","表单页面")
        menu.click()
        menu = self.selenium_mode.find_text_from(".i-layout-menu-side-title-text","基础表单")
        menu.click()






