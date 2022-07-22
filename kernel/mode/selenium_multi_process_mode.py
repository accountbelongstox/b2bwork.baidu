import random
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
import random
import pprint
from kernel.base_class.load_module_class import *
# 为保证 driver 能正常打开

class SeleniumMultiProcessMode(BaseClass):
    __threads = {}

    def __init__(self,args):
        pass

    def create_thread(self, target=None, args=(), thread_id=None, thread_name=None,daemon=False):
        if thread_id == None:
            thread_id = random.random()
        thread = SeleniumThread(target, args, thread_id, thread_name,daemon)
        LoadModuleClass().attach_module_from(self,"selenium_mode")
        self.selenium_mode.main(thread,callback_module_name=thread_name)
        self.__threads[thread_name] = thread
        self.__threads[thread_id] = thread
        return thread

    def get_thread(self, thread_ident):
        if thread_ident in self.__threads:
            return self.__threads[thread_ident]
        else:
            print(f"Not Found thread: {thread_ident} in selenium_multi_process_mode.")
            return None

    def getDaemon(self, thread_ident):
        th = self.get_thread(thread_ident)
        daemon = th.getDaemon()
        return daemon
    def setDaemon(self, thread_ident,daemon):
        th = self.get_thread(thread_ident)
        th.setDaemon(daemon)

    def is_alive(self, thread_ident):
        th = self.get_thread(thread_ident)
        r = th.is_alive()
        return r

    def run(self, thread_ident):
        th = self.get_thread(thread_ident)
        return th.run()

    def join(self, thread_ident):
        th = self.get_thread(thread_ident)
        return th.join()

    def send(self, thread_ident,data):
        th = self.get_thread(thread_ident)
        th.send(data)

    def set(self, thread_ident,name,data):
        th = self.get_thread(thread_ident)
        th.set(name,data)


class SeleniumThread(threading.Thread):  # 继承父类threading.Thread
    __driver = None
    __loginUser = None
    __loginPwd = None
    __data_fields = None
    __init_driver_open = True

    def __init__(self, target, args, thread_id, thread_name,daemon):
        threading.Thread.__init__(self,name=thread_name,daemon=daemon)
        self.target = target
        self.args = args
        self.thread_id = thread_id
        self.name = thread_name
        self.__send_args = Queue()
        self.__loginUser = args["login"]["loginUser"]
        self.__loginPwd = args["login"]["loginPwd"]
        self.__data_fields = args["data_fields"]
        self.__config = args

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        if self.target != None:
            self.target(self.args)
        else:
            self.__driver = self.selenium_mode.get_driver()
            self.url_open_active()
        # self.selenium_mode.open_url("http://localhost")

    def get_id(self):
        return self.thread_id
    def set_id(self,thread_id):
        self.thread_id = thread_id
        return self.thread_id

    def set(self,name,data):
        self.__dict__[name] = data

    def send(self,send_args):
        self.__send_args.put(send_args)

    def url_open_active(self):
        active_period = self.__config["login"]["login_active"]["active_period"]
        while True:
            #开始活动检查标志
            self.__config["login"]["active_check"] = True
            print("processing active checking.")
            if self.__config["login"]["mustLogin"]:
                isLogin = self.login_check()
                self.__config["login"]["isLogin"] = isLogin
                if not isLogin:
                    print(f"is not isLogin")
                    self.__config["login"]["isLogin"] = self.login_and_verify()
            if self.__config["login"]["isLogin"]:
                self.logined_acitve()
            #关闭活动检查标志
            self.__config["login"]["active_check"] = False
            #开始睡眠
            time.sleep(active_period)

    def login_check(self):
        self.__driver.refresh()
        loginVerifyURL = self.__config["login"]["loginVerifyURL"]
        current_url = self.__driver.current_url
        print(f"current_url {current_url}")
        if current_url.find(loginVerifyURL) == 0:
            print(f"loading_verify successfully.")
            return True
        else:
            return False

    def login_and_verify(self):
        self.login()
        is_loading = self.login_verify()
        self.login_pre()
        return is_loading

    def login_pre(self):
        login_pre = self.__config["login"]["login_pre"]
        if "clicks" in login_pre:
            clicks = login_pre["clicks"]
            for click_selector in clicks:
                click_element = self.selenium_mode.find_element_wait( click_selector)
                click_element.click()

    def login(self):
        userInput = self.__config["login"]["userInput"]
        pwdInput = self.__config["login"]["pwdInput"]
        submit = self.__config["login"]["submit"]
        loginURL = self.__config["login"]["loginURL"]
        loginUser = self.__loginUser
        loginPwd = self.__loginPwd
        self.init_driver(loginURL)
        userInputElement = self.selenium_mode.find_element_wait(userInput)
        pwdInputElement = self.selenium_mode.find_element_wait(pwdInput)
        submitElement = self.selenium_mode.find_element_wait(submit)
        userInputElement.send_keys(loginUser)
        pwdInputElement.send_keys(loginPwd)
        submitElement.click()

    def login_verify(self):
        loginVerifyURL = self.__config["login"]["loginVerifyURL"]
        current_url = self.__driver.current_url
        if current_url.find(loginVerifyURL) == -1:
            print(f"login_verify successfully.")
            return True
        else:
            print(f"login_verifing current_url:{current_url} to loginVerifyURL:{loginVerifyURL} ")
            time.sleep(1)
            return self.login_verify()

    def init_driver(self,url,cb=None):
        if self.__init_driver_open == True:
            self.selenium_mode.open_url(url=url)
            print('load_JQuery loading..')
            self.selenium_mode.load_JQuery_wait()
            self.__init_driver_open = False
        else:
            len_drivers = len(self.__driver.window_handles)
            url_exists = False
            for index in range(len_drivers):
                self.__driver.switch_to.window(self.__driver.window_handles[index])
                if self.__driver.current_url.find(url) == 0:
                    url_exists = True
                    print(f"init_driver found url is {self.__driver.current_url}")
                    break
            if not url_exists:
                js = "window.open('{}','_blank');"
                self.__driver.execute_script(js.format(url))
                print(f"init_driver open url by new window for page {url}")
                self.selenium_mode.load_JQuery_wait()
        if cb != None: cb()

    def logined_acitve(self):
        active_url = self.__config["login"]["login_active"]["active_url"]
        buttons = self.__config["login"]["login_active"]["buttons"]
        self.selenium_mode.switch_to_window_by_url_and_open(active_url)
        for button_selector in buttons:
            button_selector = self.selenium_mode.find_element_wait(button_selector)
            button_selector.click()

    def get_data(self,args):
        if self.__config["login"]["active_check"]:
            time.sleep(2)
            return self.get_data(args)
        try:
            datatypes_str = args["datatypes"]
            datatypes = datatypes_str.split(',')
        except:
            getdata_result = {}
            # 如果不是当前token name请求，则跳过
            getdata_result["type"] = 0
            getdata_result["message"] = "no request name is datatype"
            getdata_result["error"] = f"no request name is datatype,datatype is {datatypes_str}"
            return getdata_result

        password = None
        if "password" in args:
            password = args["password"]
        method = None
        if "method" in args:
            method = args["method"]

        graspFields = self.__data_fields
        pprint.pprint(graspFields)
        getdata_result = {}
        for grasp_unit in graspFields:
            datatype = grasp_unit["datatype"]
            if datatype not in datatypes:
                continue
            page = grasp_unit["page"]
            self.init_driver( page)
            datas_by_class = grasp_unit["datas_by_class"]
            sentinel_selector = datas_by_class["sentinel_selector"]
            self.selenium_mode.find_elements_value_wait(sentinel_selector)
            datas = datas_by_class["datas"]
            for data in datas:
                selectors = data["selectors"]
                attr = data["attr"]
                datatype = data["datatype"]
                description = data["description"]
                for selector_value in selectors:
                    selector = selector_value["selector"]
                    selector_names = selector_value["selector_names"].split(",")
                    if attr == "value":
                        results = self.selenium_mode.find_elements_value_by_js_wait( selector)
                        get_data_unit = {}
                        for i in range( len(selector_names) ):
                            selector_name = selector_names[i]
                            selector_value = results[i]
                            get_data_unit[selector_name] = selector_value
                        getdata_result[datatype] = {
                            "description" : description,
                            "datatype" : datatype,
                            "data" : get_data_unit
                        }
                        print(f"get_data_unit {get_data_unit}")
        getdata_result["type"] = 0
        getdata_result["message"] = "successfully get data"
        getdata_result["data"] = getdata_result
        return getdata_result