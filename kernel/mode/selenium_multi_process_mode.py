import operator
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
        LoadModuleClass().attach_module_from(self,"selenium_mode")
        thread = SeleniumThread(target, args, thread_id, thread_name,daemon)
        self.selenium_mode.main(
            {
                "module":thread,
                "driver_name":thread_name,
                "headless":True
            }
        )
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
        # while True:
        #     self.__driver = self.selenium_mode.get_driver()
        #     print(f"self.__driver {self.name } -> {self.__driver}")
        #     time.sleep(1)
        # return
        active_period = self.__config["login"]["login_active"]["active_period"]
        while True:
            #开始活动检查标志
            self.__config["login"]["active_check"] = True
            print("processing active checking.")
            if self.__config["login"]["mustLogin"]:
                isLogin = self.login_check()
                self.__config["login"]["isLogin"] = isLogin
                if not isLogin:
                    self.__config["login"]["isLogin"] = self.login_and_verify()
            if self.__config["login"]["isLogin"]:
                self.logined_acitve()
            #关闭活动检查标志
            self.__config["login"]["active_check"] = False
            #开始睡眠
            time.sleep(active_period)

    def login_check(self):
        if self.__driver is None:
            self.__driver = self.selenium_mode.get_driver()
        #如果有验证页，则说明已经登陆过可能已过期，则刷新
        loginVerifyURL = self.__config["login"]["loginVerifyURL"]
        url_exists = self.selenium_mode.find_url_from_driver_handles(loginVerifyURL)
        print(f"login_check url_exists {url_exists}")
        if url_exists != -1:
            self.__driver.refresh()
            #如果刷新过后页面依然存在，则说明未过期
            url_exists = self.selenium_mode.find_url_from_driver_handles(loginVerifyURL)
            if url_exists != -1:
                return True
            else:
                return False
        else:
            return False

    def login_and_verify(self):
        self.login()
        is_login = self.login_verify_continue()
        self.login_pre()
        return is_login

    def login_pre(self):
        login_pre = self.__config["login"]["login_pre"]
        if "clicks" in login_pre:
            clicks = login_pre["clicks"]
            for click_selector in clicks:
                click_element = self.selenium_mode.find_element_wait( click_selector)
                click_element.click()

    def login_click(self,x_offset,y_offset):
        move_to_element = self.selenium_mode.find_elements('.vcode-spin-button',is_beautifulsoup=True)
        move_to_element = move_to_element[0][0]
        id = move_to_element["id"]
        id = f"#{id}"
        self.selenium_mode.move_to_element(id,x_offset,y_offset)

    def login(self):
        userInput = self.__config["login"]["userInput"]
        pwdInput = self.__config["login"]["pwdInput"]
        submit = self.__config["login"]["submit"]
        loginURL = self.__config["login"]["loginURL"]
        loginUser = self.__loginUser
        loginPwd = self.__loginPwd
        self.selenium_mode.open_url_as_new_window(loginURL)
        userInputElement = self.selenium_mode.find_element_wait(userInput)
        pwdInputElement = self.selenium_mode.find_element_wait(pwdInput)
        submitElement = self.selenium_mode.find_element_wait(submit)
        userInputElement.send_keys(loginUser)
        pwdInputElement.send_keys(loginPwd)
        submitElement.click()

    def login_verify_continue(self):
        loginVerifyURL = self.__config["login"]["loginVerifyURL"]
        if operator.__eq__(self.__driver.current_url,loginVerifyURL):
            return True
        else:
            print(f"login_verify_continue check is :{self.__driver.current_url} to {loginVerifyURL} ")
            time.sleep(1)
            return self.login_verify_continue()
    #
    # def init_driver(self,url,cb=None):
    #     if self.__init_driver_open == True:
    #         self.selenium_mode.open_url(url=url)
    #         print('load_JQuery loading..')
    #         self.selenium_mode.load_JQuery_wait()
    #         self.__init_driver_open = False
    #     else:
    #         len_drivers = len(self.__driver.window_handles)
    #         url_exists = False
    #         for index in range(len_drivers):
    #             self.__driver.switch_to.window(self.__driver.window_handles[index])
    #             if self.__driver.current_url.find(url) == 0:
    #                 url_exists = True
    #                 print(f"init_driver found url is {self.__driver.current_url}")
    #                 break
    #         if not url_exists:
    #             js = "window.open('{}','_blank');"
    #             self.__driver.execute_script(js.format(url))
    #             print(f"init_driver open url by new window for page {url}")
    #             self.selenium_mode.load_JQuery_wait()
    #     if cb != None: cb()

    def logined_acitve(self):
        active_url = self.__config["login"]["login_active"]["active_url"]
        buttons = self.__config["login"]["login_active"]["buttons"]
        self.selenium_mode.open_url_as_new_window(active_url)
        for button_selector in buttons:
            button_selector = self.selenium_mode.find_element_wait(button_selector)
            button_selector.click()

    def get_html_resource(self):
        #vcode-spin-img
        html = self.__driver.page_source
        html += "取得滑动登陆验证距离的javascript代码"
        return html

    def get_login_verify_html(self):
        if not self.login_check():
            self.__driver.refresh()
            self.login()
        #vcode-spin-img
        time.sleep(3)
        selector_css = self.selenium_mode.find_element(".vcode-spin-img",is_beautifulsoup=True)
        if len(selector_css) > 0:
            # links = self.selenium_mode.find_element("link",is_beautifulsoup=True)
            # link_len = len(links)
            # current_url_parse = urlparse(self.__driver.current_url)
            # current_url = f"{current_url_parse.scheme}://{current_url_parse.netloc}"
            # insert_html_link_as_style = ''
            # for index in range(link_len):
            #     try:
            #         link = links[index]
            #         href = link["href"]
            #         link["href"] = current_url + href
            #         if os.path.splitext(link["href"])[1] == '.css':
            #             insert_html_link_as_style += str(link)
            #     except:
            #         pass
            vcode_spin_img = selector_css[0]
            # vcode_spin_img = insert_html_link_as_style + str(vcode_spin_img)
            vcode_spin_img = vcode_spin_img["src"]
        else:
            vcode_spin_img = self.selenium_mode.find_html_wait()
        return vcode_spin_img

    def get_data(self,args):
        if self.__config["login"]["active_check"]:
            time.sleep(2)
            return self.get_data(args)
        getdata_result = {}
        try:
            datatypes_str = args["datatypes"]
            datatypes = datatypes_str.split(',')
            getdata_result["type"] = 0
            getdata_result["message"] = "successfully get data"
        except:
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
        fields_data = []
        pprint.pprint(graspFields)
        for grasp_unit in graspFields:
            datatype = grasp_unit["datatype"]
            if datatype not in datatypes:
                continue
            page = grasp_unit["page"]
            self.selenium_mode.open_url_as_new_window( page , loadJQuery=True)
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
                        fields_data.append({
                            "datatype" : datatype,
                            "description" : description,
                            "data" : get_data_unit
                        })
                        print(f"get_data_unit {get_data_unit}")
        getdata_result["data"] = fields_data
        return getdata_result