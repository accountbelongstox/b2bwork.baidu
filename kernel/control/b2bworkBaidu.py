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
        pass

    def main(self,argv):
        self.__config = self.get_config()
        self.multi_browser_init()
        # pprint.pprint(self.__config)
        # e = ThreadPoolExecutor(max_workers=2)
        # e.submit(self.network_list)
        # e.submit(self.active)
        # e.set_daemon(True)
        pass

    def get_config(self):
        data_serialization_file = "b2bwork_baidu_account_data.list"
        config = {
            # 多账号支持,会启动多线程多个浏览器, 设置在下面
            # "multiaccount_support": True,
            "login": {
                "mustLogin": True,  # 是否需要预登陆
                "isLogin": False,  # 是否已经登陆
                "active_check": False,  # 活动检查
                "loadURL": "https://b2bwork.baidu.com/login?redirect=https%3A%2F%2Fb2bwork.baidu.com%2Fdashboard",
                "loadingVerifyURL": "https://b2bwork.baidu.com/login",
                "loadUser": "zsw100023649",
                "loadPwd": "Mts77066.",
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
                    "name": "shop_score",
                    "description": "店铺评分",
                    "page": "https://b2bwork.baidu.com/dashboard",
                    "datas_by_class": {
                        "sentinel_selector": """//div[@class="shop-diagnose"]/p""",
                        "datas": [
                            {
                                "name": "shop_score",
                                "description": "店铺评分",
                                "selectors": [
                                    {
                                        "selector_names": "店铺评分",
                                        "selector": ".shop-diagnose p"
                                    }
                                ],
                                "attr": "value"
                            }, {
                                "name": "commodity_management",
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
                    "name": "smart_business_opportunity",
                    "description": "智慧商机",
                    "page": "https://b2bwork.baidu.com/service/business/index?scrollTop=0",
                    "datas_by_class": {
                        "sentinel_selector": """//span[@class="el-tooltip"]""",
                        "datas": [
                            {
                                "name": "core_data",
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
                #         "loadUser": "zsw100023649",
                #         "loadPwd": "Mts77066."
                #     },
                #     "data_fields": []
                # }
                # ],
                self.db_common.unserialization(data_serialization_file),
                # {
                #     "login": {
                #         "loadUser": "zsw100023649",
                #         "loadPwd": "Mts77066."
                #     },
                #     "data_fields": []
                # }
        }
        return config

    @flask_app.route('/manager')
    @flask_app.route('/manager/<name>')
    # @mimerender(
    #     default = 'html',
    #     xml=lambda message: '<message>%s</message>' % message,
    #     json = lambda message: json.dumps(message),
    #     html = lambda message: message,
    #     txt = lambda message: message
    # )
    def login_manager(name=None):
        self = LoadModuleClass().add_module("control","b2bworkBaidu",[])
        return render_template("manager.html")

    @flask_app.route('/api')
    def api():
        #使用类加载器对类附加新类
        #用于第三方调用接口时没有附加方法的问题
        self = LoadModuleClass().add_module("control","b2bworkBaidu",[])
        method = flask_request.args.get('method')
        name = flask_request.args.get('name')
        username = flask_request.args.get('username')
        password = flask_request.args.get('password')
        url_for("static",filename="css/style.css",)
        data = self.get_data(name)
        return data

    def network_list(self,run_port=None):
        if run_port is not None:
            port = run_port
        else:
            port = 18800
        print(f'startup Flask app server. Listing port is {port}')
        flask_app.run(port=port,host="0.0.0.0")

    def f(self,arg):
        p = arg[0]
        name = "test"
        left, right = p
        left.close()
        while True:
            try:
                baozi = right.recv()
                print('%s 收到包子:%s' % (name, baozi))
            except EOFError:
                right.close()
                break
    def ff(self):
        print("test")

    def multi_browser_init(self):
        self.__config = self.get_config()

        multiaccount_support = self.__config["multiaccount_support"]
        multiaccount_datas = self.__config["multiaccount_datas"]#本线程总支持的账号数
        account_max_thread = 1
        if multiaccount_support == True:
            account_max_thread = len(multiaccount_datas)  # 最大支持的打开浏览器线程数为账号数
        account_max_thread += 1 #预留一个线程给网络监听使用
        # for thread in range(account_max_thread):
        th = self.selenium_multi_process_mode.create_thread(self.ff,(("left","right"),"ab0"),thread_id=1, thread_name="Thread-1",)
        th.start()

        # pools = ThreadPoolExecutor(max_workers=account_max_thread)
        # pools.submit(self.network_list)
        # for datas in multiaccount_datas:
        #     login = datas["login"]
        #     loadPwd = datas["loadPwd"]
        #     loadUser = datas["loadUser"]
        # pools.submit(self.active,login,loadPwd)

        return


    def active(self):
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


    def get_data(self,names=None):
        if self.__config["login"]["active_check"]:
            time.sleep(2)
            return self.get_data(names)
        graspFields = self.__config["data_fields"]
        getdata_result = {}
        for grasp_unit in graspFields:
            grasp_unit_name = grasp_unit["name"]
            if names == None or grasp_unit_name not in names.split(','):
                #如果不是当前token name请求，则跳过
                getdata_result["type"] = 0
                getdata_result["message"] = "no request name"
                getdata_result["error"] = f"names is {names}"
                getdata_result["grasp_unit_name"] = grasp_unit["name"]
                getdata_result["test_data"] = names.split(',')
                continue
            page = grasp_unit["page"]
            self.init_driver( page)
            if "datas_by_class" in grasp_unit:
                datas_by_class = grasp_unit["datas_by_class"]

                sentinel_selector = datas_by_class["sentinel_selector"]
                print(f"getting sentinel_data, selector is {sentinel_selector}")
                sentinel_data = self.selenium_mode.find_elements_value_wait(self.__driver,sentinel_selector)
                print(f" get sentinel_data successfully {sentinel_data}")

                datas = datas_by_class["datas"]
                for data in datas:
                    selectors = data["selectors"]
                    attr = data["attr"]
                    name = data["name"]
                    description = data["description"]
                    for selector_value in selectors:
                        selector = selector_value["selector"]
                        selector_names = selector_value["selector_names"].split(",")
                        if attr == "value":
                            results = self.selenium_mode.find_elements_value_by_js_wait(self.__driver, selector)
                            get_data_unit = {}
                            for i in range( len(selector_names) ):
                                selector_name = selector_names[i]
                                selector_value = results[i]
                                get_data_unit[selector_name] = selector_value
                            getdata_result[name] = {
                                "description" : description,
                                "token" : name,
                                "data" : get_data_unit
                            }
        return getdata_result


    def login_check(self):
        if self.__driver == None:
            return False
        self.__driver.refresh()
        loadingVerifyURL = self.__config["login"]["loadingVerifyURL"]
        current_url = self.__driver.current_url
        if current_url.find(loadingVerifyURL) == -1:
            print(f"loading_verify successfully.")
            return True
        else:
            return False

    def login_verify(self):
        loadingVerifyURL = self.__config["login"]["loadingVerifyURL"]
        current_url = self.__driver.current_url
        if current_url.find(loadingVerifyURL) == -1:
            print(f"loading_verify successfully.")
            return True
        else:
            print(f"loading_verifing current_url:{current_url} to loadingVerifyURL:{loadingVerifyURL} ")
            time.sleep(1)
            return self.login_verify()

    def login(self):
        userInput = self.__config["login"]["userInput"]
        pwdInput = self.__config["login"]["pwdInput"]
        submit = self.__config["login"]["submit"]
        loadURL = self.__config["login"]["loadURL"]
        loadUser = self.__config["login"]["loadUser"]
        loadPwd = self.__config["login"]["loadPwd"]
        self.init_driver(loadURL)
        userInputElement = self.selenium_mode.find_element_wait(self.__driver,userInput)
        pwdInputElement = self.selenium_mode.find_element_wait(self.__driver,pwdInput)
        submitElement = self.selenium_mode.find_element_wait(self.__driver,submit)
        userInputElement.send_keys(loadUser)
        pwdInputElement.send_keys(loadPwd)
        submitElement.click()

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
                click_element = self.selenium_mode.find_element_wait(self.__driver, click_selector)
                click_element.click()

    def logined_acitve(self):
        active_url = self.__config["login"]["login_active"]["active_url"]
        buttons = self.__config["login"]["login_active"]["buttons"]
        self.selenium_mode.switch_to_window_by_url_and_open(self.__driver,active_url)
        for button_selector in buttons:
            button_selector = self.selenium_mode.find_element_wait(self.__driver,button_selector)
            button_selector.click()

    def init_driver_local_test(self,html_name="index.html"):
        self.__driver = self.selenium_mode.open_local_html_to_beautifulsoup(html_name)

    def init_driver(self,url=None,cb=None):
        if self.__driver == None:
            if url != None:
                self.__driver = self.selenium_mode.open_url(url=url,empty_driver=False)
                print('load_JQuery loading..')
                self.selenium_mode.load_JQuery_wait(self.__driver)
            else:
                self.__driver = self.selenium_mode.get_empty_driver()
        else:
            js = "window.open('{}','_blank');"
            self.__driver.execute_script(js.format(url))
            index = (len(self.__driver.window_handles) - 1)
            print(f"self.__driver.switch_to.window to {index}")
            self.__driver.switch_to.window(self.__driver.window_handles[index])
            self.selenium_mode.load_JQuery_wait(self.__driver)
        if cb != None: cb()

    def start_thread_for_scan_trade_tick_list(self,click=True):
        #等待元素出现
        self.wait_and_find_data_token_names(click)
        #初始化历史数据列表，如果有的话。如果没有则等到开始抓取
        self.init_trade_historical_list()
        thread_pool = ThreadPoolExecutor(max_workers=1)
        thread_runIndes = 0
        change_task_test =[]
        thread_time = time.thread_time()
        while True:
            if len(change_task_test) == 0:
                thread_name=f"scratch-tread-{thread_runIndes}"
                save_to_mangodb = (thread_runIndes % 3  == 0)
                print( f" New tick {thread_name}/ thread_time:{thread_time}/ save to mangoDB:{save_to_mangodb} running.")
                change_task_test.append(
                    (
                        thread_name,
                        save_to_mangodb,
                        thread_time
                    )
                )
            task = thread_pool.submit(self.get_change_run, change_task_test.pop())
            thread_runIndes += 1
            task.result()

    def get_change_run(self,data):
        thread_name = data[0]
        is_serialize = data[1]
        thread_time = data[2]
        scan_trade_tick_list = self.scan_trade_tick_list()
        self.set_trade_categories(scan_trade_tick_list)
        for trade_item_dict in scan_trade_tick_list:
            short_name = trade_item_dict["short_name"]
            #获取一个历史数据，该历史数据包含一该类型项的一次完整的抓取
            grasp_historical_pop = self.get_trade_historical_list_pop(short_name)
            is_rise_changed = self.trade_rise_is_change(trade_item_dict,grasp_historical_pop)
            if is_rise_changed:
                self.set_trade_historical_list(short_name,trade_item_dict)
        if is_serialize : self.save_okx_exchange_rise()
        print(f"Count for change premium data are {len(self.__premium_grasp_listtmp_)} items." )
        return True

    def is_beautifulsoup(self):
        if self.__driver.__class__.__name__.__eq__("BeautifulSoup"):
            return True
        else:
            return False

    def wait_and_find_data_token_names(self,click=False):
        is_beautifulsoup = self.is_beautifulsoup()
        if  is_beautifulsoup is not True:
            WebDriverWait(self.__driver, 0).until(EC.presence_of_element_located( (By.CSS_SELECTOR, '''[data-token-name]''') ))
        if click:
            change_click = self.selenium_mode.find_text_from(self.__driver, "//*[@data-clk]", "Change")
            change_click.click()
        if self.__allPremium == None:
            # self.__allPremium = self.__driver.find_elements(By.XPATH,'//*[@data-token-name|@data-id]')
            self.__allPremium = self.selenium_mode.find_elements(self.__driver,'//*[@data-token-name|@data-id]')
        return self.__allPremium

    def trade_rise_is_change(self,tick_scratch_data,grasp_historical_pop):
        print(tick_scratch_data,grasp_historical_pop)
        tick_short_name = tick_scratch_data['short_name']
        historical_pop_short_name = grasp_historical_pop['short_name']
        tick_change = tick_scratch_data['change']
        historical_pop_change = grasp_historical_pop['change']
        is_likely_type = tick_short_name.__eq__(historical_pop_short_name)
        is_rise_changed = (tick_change != historical_pop_change)
        is_rise_changed = (is_likely_type and is_rise_changed)
        if is_rise_changed:
            primitive_price = tick_scratch_data["primitive_price"]
            last_num = tick_scratch_data["last_num"]
            print(f"Changing massage : {tick_short_name} is changed! price:({primitive_price}->{last_num}) {historical_pop_change}:( to {tick_change})")
        return is_rise_changed


    def scan_trade_tick_list(self):
        scan_trade_tick_list = []
        allPremium = self.__allPremium
        print( len(allPremium) )
        for ele in allPremium:
            print( ele.text)
            coin_infos = ele.text.split("\n")
            short_name = coin_infos[0]
            full_name = coin_infos[1]
            last_num = coin_infos[2]
            last_price_num = float(last_num[1:].replace(r",", ""))
            change_partial = coin_infos[3].split(" ")
            change = change_partial[0]
            change_sign = change[0]
            change_number = float(change[1:-1])
            if change_sign == "+":
                primitive_price = last_price_num / (1 + change_number / 100)
            elif change_sign == "-":
                primitive_price = last_price_num * (1 - change_number)
            market_cap = change_partial[1]
            c_time = time.strftime("%Y-%m-%d %H:%m:%S",time.gmtime())
            scan_trade_tick_list.append(
                {
                    "short_name": short_name,
                    "full_name": full_name,
                    "last_num": last_num,
                    "last_price_num": last_price_num,
                    "change_sign": change_sign,
                    "change": change,
                    "primitive_price": primitive_price,
                    "market_cap": market_cap,
                    "time": c_time,
                    "save_db": False
                }
            )
        return scan_trade_tick_list

    def tran_trade_categories(self,rise_tick_datas=None):
        categories = []
        if rise_tick_datas != None:
            rise_tick_datas = [str(x["short_name"]) for x in rise_tick_datas]
            for short_name in rise_tick_datas:
                categories.append(short_name)
        return categories


    def set_trade_categories(self,rise_tick_datas=None,sava_to_mongodb=False):
        daname = "list_trade_categories"
        mongodb_daname = "okx_list_trade_categories"
        categories = self.db_common.get_redis(daname)
        if rise_tick_datas == None:
            #如果redis没有缓存项目类的数据，则从mongodb读取
            if len(categories) == 0:
                categories = self.db_common.read_data_to(mongodb_daname,{})
                #从mongodb读取的数据并存入 redis.
                self.db_common.set_redis({
                    daname: categories
                })
        else:
            tick_categories = self.tran_trade_categories(rise_tick_datas)
            is_new_type_itme = False
            for short_name in tick_categories:
                if short_name not in categories:
                    is_new_type_itme = True
                    categories.append(short_name)
                    self.new_type_item(short_name,rise_tick_datas)
            if is_new_type_itme:
                self.db_common.set_redis({
                    daname: categories
                })
        self.__categories_trade_list = categories
        return categories

    def new_type_item(self,short_name,rise_tick_datas):
        for tick_data in rise_tick_datas:
            if short_name in tick_data:
                new_type_name = tick_data[short_name]
                print(f'new typeItem {new_type_name}')
                #TODO 发现新元素后的操作写在这里。
        pass


    def init_trade_historical_list(self):
        print("init trade historical list!")
        categories = self.set_trade_categories()
        if len(categories) == 0:
            scan_trade_tick_list = self.scan_trade_tick_list()
            categories = self.set_trade_categories(scan_trade_tick_list)
            print("categories",categories)
        for short_name in categories:
            if len(self.get_trade_historical_list(short_name)) == 0:
                all_premium_grasp_dict = self.load_trade_historical(max=1000)
                print(type(all_premium_grasp_dict))
                for trade_name,tick_scratch_list in all_premium_grasp_dict.items():
                    self.set_trade_historical_list(trade_name,tick_scratch_list)

    def get_trade_historical_list_pop(self,short_name): # trade_historical_list
        redis_name = self.get_redis_trade_historical_list_name(short_name)
        type_list = self.db_common.get_redis(redis_name,[0,0])
        print(f"get_trade_historical_list_pop {type(type_list)}{len(type_list)}")
        type_list = json.loads(type_list)
        print(f"get_trade_historical_list_pop {type(type_list)}{len(type_list)}")
        return type_list
    def get_trade_historical_list(self,short_name,pop=[0,-1]):
        redis_name = self.get_redis_trade_historical_list_name(short_name)
        type_list = self.db_common.get_redis(redis_name,pop)
        if type(type_list) == str:
            type_list = json.loads(type_list)
        return type_list
    def set_trade_historical_list(self,trade_name,tick_scratch_list):
        redis_name = self.get_redis_trade_historical_list_name(trade_name)
        self.db_common.set_redis({
            redis_name:json.dumps(tick_scratch_list)
        })
    def get_redis_trade_historical_list_name(self,short_name):
        return f"{self.__redis_trade_item_dict_pre}{short_name}"

    def load_trade_historical(self,max=1000,short_name=None):
        print( " load_okx_exchange_rise is exec .~")
        collection_name = self.__trade_historical_mongodb
        datas = []
        scan_trade_tick_list = self.scan_trade_tick_list()
        if self.__save_project_as_mongodb:
            if short_name != None:
                data = self.db_common.read_data_to(collection_name,{
                    "short_name":short_name,
                    "limit": max
                })
                datas = data
            else:
                #使用mongodb存储
                for trade_item_dict in scan_trade_tick_list:
                    short_name = trade_item_dict["short_name"]
                    data = self.db_common.read_data_to(collection_name,{
                        "short_name":short_name,
                        "limit": max
                    })
                    datas += data
        else:
            #使用本地文件序列化
            datas = self.file_common.unserialization(self.__exchangeDataFile)
            if datas == None:
                datas = []
        premium_grasp_list = {}
        for data in datas:
            short_name = data["short_name"]
            if premium_grasp_list.get(short_name) == None:
                premium_grasp_list[short_name] = []
            premium_grasp_list[short_name].append(data)
        return premium_grasp_list

    def categories_rise_sort(self,lg="%7"):
        """
        对可交易项目进行幅度排序。
        :param lg:
        :return:
        """
        lg = lg[1:]
        lg = float(lg)
        short_list = []
        trade_categories = self.__categories_trade_list
        for short_name in trade_categories:
            trade_info = self.get_trade_historical_list_pop(short_name)
            if trade_info["change"] >= lg : short_list.append(trade_info)
        short_list.sort(key = lambda x : x["change"], reverse = True)
        return short_list

    def monitor_trade_rises(self):
        categories_rise_sort = self.categories_rise_sort("%7")
        #调用多线程打开监控页面
        max_workers = len(categories_rise_sort)
        # categories_rise_sort = [(cate) for cate in categories_rise_sort]
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            pool.submit(self.oversee_trade_data,categories_rise_sort)



    def oversee_trade_data(self, category_rise):
        short_name = category_rise["short_name"]
        short_name = short_name.lower()
        trade_spot_url = f"https://www.okx.com/trade-spot/{short_name}-usdt"
        driver = self.selenium_mode.open_url(trade_spot_url, empty_driver=True)

        while category_rise["change"] > 7:
            self.selenium_mode.execute_js(driver,"monitor_trade_data.js")
        return True

    def save_okx_exchange_rise(self):
        #提取未保存数据
        grasp_listtmp = self.set_grasp_listtmp()
        #设置保存标志位
        for item in grasp_listtmp:
            item["save_db"] = True

        if self.__save_project_as_mongodb:
            #使用mongodb存储
            print( f"save_project_as_mongodb to {len(grasp_listtmp)} items.~")
            self.db_common.save_data_to("okx_exchange_rise",grasp_listtmp)
        else:
            #使用本地文件序列化
            print( f"file serialization to {len(grasp_listtmp)} items.~")
            obj = self.file_common.unserialization(self.__exchangeDataFile)
            if obj == None:
                obj = []
            obj = obj + grasp_listtmp
            self.file_common.serialization(obj, self.__exchangeDataFile)
        self.set_grasp_listtmp(clear=True)

    def rise_tick_data_pop(self,short_name):
        for c_tick in self.__change_list_tick:
            # 如果tick还没有添加,或者价格有变动,则压入tick并将上一次推入总数据列中.
            if c_tick["short_name"].__eq__(short_name):
                self.__change_list_tick.remove(c_tick)
                return c_tick
        return None
    #
    # def get_trade_link(self,item_name):
    #     return f"https://www.okx.com/trade-spot/{item_name}"
    #









