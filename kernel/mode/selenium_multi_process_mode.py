import shutil
from kernel.base_class.base_class import *
import os
import re
import time
import lxml.html
from lxml import etree
from lxml.cssselect import CSSSelector
from selenium import webdriver
from selenium.webdriver.common.by import By
from queue import Queue
from urllib.parse import urlparse
# from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import threading
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.common.exceptions import NoSuchElementException
import sched
import pprint

# 为保证 driver 能正常打开
driver = None
webdriver_ = webdriver
threadLock = threading.Lock()

class SeleniumMultiProcessMode(BaseClass):
    __threads = []

    def __init__(self):
        pass

    def create_thread(self, fn=None, args=(), thread_id=None, thread_name=None,daemon=False):
        thread = NewThread(fn, args, thread_id, thread_name,daemon)
        self.__threads.append(thread)
        return thread

    def get_thread(self, thread_ident):
        is_id = True
        if type(thread_ident) == str:
            is_id = False

        for thread in self.__threads:
            if is_id == True:
                thread_c = thread.get_name()
            else:
                thread_c = thread.get_id()
            if thread_c == thread_ident:
                return thread
        return None

    def getDaemon(self, thread_ident):
        th = self.thread_name(thread_ident)
        daemon = th.getDaemon()
        return daemon
    def setDaemon(self, thread_ident,daemon):
        th = self.thread_name(thread_ident)
        th.setDaemon(daemon)

    def is_alive(self, thread_ident):
        th = self.thread_name(thread_ident)
        r = th.is_alive()
        return r

    def run(self, thread_ident):
        th = self.thread_name(thread_ident)
        return th.run()

    def join(self, thread_ident):
        th = self.thread_name(thread_ident)
        return th.join()

    def send(self, thread_ident,data):
        th = self.thread_name(thread_ident)
        th.send(data)


class NewThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, fn, args, thread_id, thread_name,daemon):
        threading.Thread.__init__(self,name=thread_name,daemon=daemon)
        self.fn = fn
        self.args = args
        self.thread_id = thread_id
        self.name = thread_name
        self.__send_args = Queue()

    def run(self, ):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        pprint.pprint(dir(threading.Thread))
        if self.fn != None:
            self.fn(self.args)
        else:
            print("Not give Function")

    def get_id(self):
        return self.thread_id
    def set_id(self,thread_id):
        self.thread_id = thread_id
        return self.thread_id


    def send(self,send_args):
        self.__send_args.put(send_args)