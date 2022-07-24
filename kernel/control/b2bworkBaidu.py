#import os
import json
# import os.path
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
# from multiprocessing import Process
from flask import Flask,url_for,render_template
from flask import request as flask_request
from kernel.base_class.load_module_class import *
import mimerender
from multiprocessing import Process, Pipe
import pprint
#
# from twisted.web import proxy, http
# from twisted.internet import reactor
# from twisted.python import log
# import sys
# #
# # log.startLogging(sys.stdout)
# #

mimerender = mimerender.FlaskMimeRender()
flask_app = Flask(__name__)
app_self = None

class B2Bworkbaidu(BaseClass):
    __isRedis = True
    __exchangeDataFile = "exchangeData.list"
    __premium_grasp_listtmp_ = []
    __change_list_tick = []
    __categories_trade_list = []
    __trade_historical_mongodb = "list_trade_historical"
    __redis_trade_item_dict_pre = "list_okx_"
    __config = None
    __driver = None

    # 标准化
    # categories_trade_list =
    # scan_trade_tick_list =
    # trade_item_dict =
    # trade_historical_list =
    # trade_historical_list =
    #
    # """

    def __init__(self,argv):
        global app_self
        app_self = self
        # self.selenium_mode.create_single(self)
        pass

    def main(self,argv):
        self.multi_browser_init()
        e = ThreadPoolExecutor(max_workers=1)
        e.submit(self.network_list)
        # e.submit(self.active)
        pass

    @flask_app.route('/api_login_manager')
    # @mimerender(
    #     default = 'html',
    #     xml=lambda message: '<message>%s</message>' % message,
    #     json = lambda message: json.dumps(message),
    #     html = lambda message: message,
    #     txt = lambda message: message
    # )
    def login_manager():
        url_for("static",filename="css/style.css",)
        self = app_self
        accounts = self.db_common.unserialization(self.get_account_serialization_file())
        manager_data = {}
        manager_data["accounts_list"] = []
        not_login = 0
        data_fields = self.get_config("data_fields")

        for data in data_fields:
            datatype = data["datatype"]
            description = data["description"]
            # {
            #     "datatype":datatype,
            #     "description":description
            # }
        #datatype
        for account in accounts:
            loginUser = account["login"]["loginUser"]
            th = self.selenium_multi_process_mode.get_thread(loginUser)
            is_login = th.login_check()
            if not is_login:
                not_login +=1
            manager_data["accounts_list"].append({
                "username":loginUser,
                "islogin":is_login,
            })
        manager_data["not_login"] = not_login
        return render_template("manager.html",manager_data=manager_data)

    @flask_app.route('/get_login_verify')
    def get_login_verify():
        self = app_self
        x_offset = flask_request.args.get('x_offset')
        username = flask_request.args.get('username')
        th = self.selenium_multi_process_mode.get_thread(username)
        if x_offset is not None:
            y_offset = flask_request.args.get('y_offset')
            x_offset = int(x_offset)
            y_offset = int(y_offset)
            print(f" x_offset {x_offset} y_offset {y_offset}")
            th.login_click(x_offset,y_offset)
            time.sleep(5)
            is_login = th.login_check()
            if is_login:
                return "0"
            else:
                return "null"
        else:
            html = th.get_login_verify_html()
            return html

    @flask_app.route('/api')
    def api():
        #使用类加载器对类附加新类
        #用于第三方调用接口时没有附加方法的问题
        self = app_self
        method = flask_request.args.get('method')
        datatypes = flask_request.args.get('datatypes')
        username = flask_request.args.get('username')
        password = flask_request.args.get('password')
        th = self.selenium_multi_process_mode.get_thread(username)
        if username == None:
            data = {
                "message": "no username",
                "type": None
            }
            return data
        if datatypes == None:
            data = {
                "message": "no datatypes",
                "type": None
            }
            return data
        data = th.get_data({
            "method":method,
            "datatypes":datatypes
        })
        print(f"data{data}")
        return data

    def get_account_config(self,account_name,keys):
        if type(keys) == str:
            keys = [keys]
        if self.__config["multiaccount_support"] == True:
            multiaccount_datas = self.__config["multiaccount_datas"]
            # 有多账号的时候从多账号中读配置
            # 如果多账号没有配置则读总配置
            # 账号单独配置覆盖主配置
            account_config = None
            print(f"account_name {account_name}")
            for account in multiaccount_datas:
                print(f"account {account}")
                login = account["login"]
                if account_name == login["loginUser"]:
                    account_config = account
            if account_config == None:
                print(f"Not found account:{account_name} in multiaccount_datas in get_account_set.")
                return None
            value_as_multiaccounts = None
            value_as_config = None
            value = None
            for key in keys:
                exist_multiaccounts = True
                if value_as_multiaccounts == None:
                    try:
                        value_as_multiaccounts = account_config[key]
                    except:
                        exist_multiaccounts = False
                elif key in value_as_multiaccounts:
                    value_as_multiaccounts = value_as_multiaccounts[key]
                else:
                    exist_multiaccounts = False

                exist_config = True
                if value_as_config == None:
                    value_as_config = self.__config[key]
                elif key in value_as_config:
                    value_as_config = value_as_config[key]
                else:
                    exist_config = False

                if exist_multiaccounts:
                    value = value_as_multiaccounts
                elif exist_config:
                    value = value_as_config
                else:
                    print(f"key {key}")
                    print(f"value_as_config {value_as_config}")
                    value = None
                    break
            return value
        else:
            #没有多账号直接从配置中读配置
            if account_name == self.__config["loginUser"]:
                value = None
                for key in keys:
                    if value == None:
                        value = self.__config[key]
                    else:
                        value = value[key]
                return value
            else:
                print(f"Not found account:{account_name} in self.__config['loginUser'] in get_account_set.")
                return None

    def init_config(self):
        config = {
            # 多账号支持,会启动多线程多个浏览器, 设置在下面
            # "multiaccount_support": True,
            "login": {
                "mustLogin": True,  # 是否需要预登陆
                "isLogin": False,  # 是否已经登陆
                "active_check": False,  # 活动检查
                "loginURL": "https://b2bwork.baidu.com/login",
                "loginVerifyURL": "https://b2bwork.baidu.com/dashboard",

                # "loginUser": "zsw100023649",
                # "loginPwd": "Mts77066.",
                "userInput": """//*[@id="uc-common-account"]""",
                "pwdInput": """//*[@id="ucsl-password-edit"]""",
                "submit": "#submit-form",
                "login_active": {
                    "active_url": "https://b2bwork.baidu.com/dashboard",
                    "active_period": 60,
                    "buttons": [
                        """//*[@id="app"]/div/div[2]/div[1]/div[1]/div/ul/div[3]/li/ul/div[1]/a/li/span""",
                        """//*[@id="app"]/div/div[2]/div[1]/div[1]/div/ul/div[1]/a/li/span"""
                    ]
                },
                "login_pre": {
                    "clicks": [".primary"]
                }
            },
            "data_fields": [
                {
                    "datatype": "shop_score",
                    "description": "店铺评分",
                    "page": "https://b2bwork.baidu.com/dashboard",
                    "datas_by_class": {
                        "sentinel_selector": """//div[@class="shop-diagnose"]/p""",
                        "datas": [
                            {
                                "datatype": "shop_score",
                                "description": "店铺评分",
                                "selectors": [
                                    {
                                        "selector_names": "店铺评分",
                                        "selector": ".shop-diagnose p"
                                    }
                                ],
                                "attr": "value"
                            }, {
                                "datatype": "commodity_management",
                                "description": "商品管理",
                                "selectors": [
                                    {
                                        "selector_names": "商品总数,交易商品,在售中,已下架,已驳回",
                                        "selector": ".pm-data .item-data"
                                    }
                                ],
                                "attr": "value"
                            }
                        ]
                    }
                },
                {
                    "datatype": "smart_business_opportunity",
                    "description": "智慧商机",
                    "page": "https://b2bwork.baidu.com/service/business/index?scrollTop=0",
                    "datas_by_class": {
                        "sentinel_selector": '//*[@class="el-tooltip"]',
                        "datas": [
                            {
                                "datatype": "core_data",
                                "description": "核心数据",
                                "selector": ".el-tooltip",
                                "selectors": [
                                    {
                                        "selector_names": "曝光量,点击量,访客数,电话量,表单量,IM数",
                                        "selector": ".el-tooltip"
                                    }
                                ],
                                "attr": "value"
                            }
                        ]
                    }
                },

            ],
            "multiaccount_support": True,  # 多账号支持,会启动多线程多个浏览器
            "multiaccount_datas":
                # [  # 多账号的数据列表，设置会覆盖父一级的设置
                # {
                #     "login": {
                #         "loginUser": "zsw100023649",
                #         "loginPwd": "Mts77066."
                #     },
                #     "data_fields": []
                # }
                # ],
                self.db_common.unserialization(self.get_account_serialization_file()),
                # {
                #     "login": {
                #         "loginUser": "zsw100023649",
                #         "loginPwd": "Mts77066."
                #     },
                #     "data_fields": []
                # }
        }
        self.__config = config
        return self.__config

    def get_account_serialization_file(self):
        return "b2bwork_baidu_account_data.list"

    def add_account_to_account(self,args):
        if type(args) == tuple:
            args = [args]
        account_data = []
        for account in args:
            try:
                loginUser = account[0]
                loginPwd = account[1]
            except:
                return None
            try:
                data_fields = account[2]
            except:
                data_fields = None
            account_item ={
                    "login": {
                        "loginUser": loginUser,
                        "loginPwd": loginPwd
                    }
                }
            if data_fields != None:
                account_item["data_fields"] = data_fields
            account_data.append(
                account_item
            )
        print(f"add_account_to_account {account_data}")
        filename = self.get_account_serialization_file()
        self.db_common.serialization( account_data,filename)
        return self.init_config()

    def get_config(self,account_name=None,keys=None):
        if self.__config == None:
            self.init_config()
        #只有account_name一项，用account_name代替key
        if (account_name != None and keys == None) \
                or\
            (account_name == None and keys != None):
            if account_name in self.__config:
                return self.__config[account_name]
            else:
                print(f"Not found {account_name} in self.__config")
                return None
        if account_name != None and keys != None:
            return self.get_account_set(account_name,keys)
        else:
            return self.init_config()

    def network_list(self,run_port=None):
        if run_port is not None:
            port = run_port
        else:
            port = 8800
        print(f'startup Flask app server. Listing port is {port}')
        flask_app.run(port=port,host="0.0.0.0")

    def multi_browser_init(self):
        # self.add_account_to_account(("zsw100023649","Mts77066."))
        
        multiaccount_support = self.get_config("multiaccount_support")
        multiaccount_datas = self.get_config("multiaccount_datas")#本线程总支持的账号数
        config = {}
        for config_k,config_v in self.__config.items():
            config[config_k] = config_v
        # print(f"multiaccount_datas",multiaccount_datas)
        account_max_thread = 1
        if multiaccount_support == True:
            account_max_thread = len(multiaccount_datas)  # 最大支持的打开浏览器线程数为账号数
        # account_max_thread += 1 #预留一个线程给网络监听使用

        for id in range(account_max_thread):
            account = multiaccount_datas[id]
            # print(account)
            login = account["login"]
            loginUser = login["loginUser"]
            # deep_key = []
            for login_k,login_v in account.items():
                if type(login_v) == dict:
                    for login_k_, login_v_ in login_v.items():
                        if type(login_v_) == dict:
                            for login_k__, login_v__ in login_v_.items():
                                if type(login_v__) == dict:
                                    for login_k___, login_v___ in login_v__.items():
                                        if type(login_v___) == dict:
                                            for login_k____, login_v____ in login_v___.items():
                                                # deep_key.append(login_k____)
                                                config[login_k][login_k_][login_k__][login_k___][login_k____] = login_v____
                                        else:config[login_k][login_k_][login_k__][login_k___] = login_v___
                                        # deep_key.append(login_k___)
                                else:config[login_k][login_k_][login_k__] = login_v__
                                # deep_key.append(login_k__)
                        else:config[login_k][login_k_] = login_v_
                        # deep_key.append(login_k_)
                else:config[login_k] = login_v
                # deep_key.append(login_k)
            # print(config)
            #     # config[login_k] = login_v
            # args = (config)
            th = self.selenium_multi_process_mode.create_thread(args=config,thread_id=id, thread_name=loginUser,)
            # th.set("__config",self.get_config())
            th.start()
        # th = self.selenium_multi_process_mode.create_thread(target=self.network_list, args=config,thread_name="network_list",)
        # # th.set("__config",self.get_config())
        # th.start()
        return

