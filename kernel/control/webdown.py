#import os
import json
import os.path
import time

from kernel.base_class.base_class import *
#import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.webdriver.support.wait import WebDriverWait
#from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
#from queue import Queue
import re


class Webdown(BaseClass):
    __downUrl = None

    def __init__(self,argv):
        pass

    def main(self,argv):
        try:
            downUrl = argv[2]
            self.__downUrl =downUrl
        except:
            print("argv[0] not found downUrl: %s" % argv)
        print("starting downUrl of website %s" % self.__downUrl)
        self.selenium_mode.down_website(self.__downUrl)
        pass