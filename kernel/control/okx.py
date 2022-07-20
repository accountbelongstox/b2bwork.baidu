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


class Okx(BaseClass):
    __startMain = "https://www.okx.com/markets/prices"
    __exchangeDataFile = "exchangeData.list"
    __premium_grasp_listtmp_ = []
    __change_list_tick = []
    __categories_trade_list = []
    __trade_historical_mongodb = "list_trade_historical"
    __redis_trade_item_dict_pre = "list_okx_"

    # 标准化
    # """
    #
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
        #TODO 测试数据库函数每个单元
        # self.set_trade_categories --ok--
        # self.init_trade_historical_list
        # self.get_trade_historical_list_pop
        # self.set_trade_historical_list
        # self.set_grasp_listtmp
        # self.load_trade_historical
        # self.save_okx_exchange_rise
        # 另外需测试db_common函数中对于不存在的表返回类型是否为None

        #TODO
        # 首先从数据库中读取100条数据
        # 如果数据过旧，超过3天则没有参考价值，直接不作为对比，而直接添加
        # 如果数据在3天以前，则可以不以上一个tick为比较
        # 每个tick对比上一轮数据，有变化则加入缓存
        # 缓存中根据游标显示读到多少数据，小于1000则再从数据库中读1000条（旧的数据），大于1则读取最新数据填充（以读取的数量+上当前游标确定游标）
        # from urllib.parse import urlparse
        # up = urlparse("http://www.jqueryfuns.com/texiao/test")

        # ../resource/5733/0.jpg
        self.selenium_mode.down_website("http://www.jqueryfuns.com")
        # self.init_driver_local_test("index.html")
        # self.init_driver(self.__startMain)
        # self.start_thread_for_scan_trade_tick_list(click=False)
        # js_path = self.selenium_mode.execute_js(self.__driver,"jquery-3.6.0.min.js")
        pass



    def init_driver_local_test(self,html_name="index.html"):
        self.__driver = self.selenium_mode.open_local_html_to_beautifulsoup(html_name)

    def init_driver(self,url=None):
        self.__driver = self.selenium_mode.get_empty_driver()
        # self.__driver = EventFiringWebDriver(self.__driver, PremiumChange())
        self.__driver = self.selenium_mode.open_url(url,empty_driver=False)

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
            datas = self.db_common.unserialization(self.__exchangeDataFile)
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
            print( f"db serialization to {len(grasp_listtmp)} items.~")
            obj = self.db_common.unserialization(self.__exchangeDataFile)
            if obj == None:
                obj = []
            obj = obj + grasp_listtmp
            self.db_common.serialization(obj, self.__exchangeDataFile)
        self.set_grasp_listtmp(clear=True)

    def rise_tick_data_pop(self,short_name):
        for c_tick in self.__change_list_tick:
            # 如果tick还没有添加,或者价格有变动,则压入tick并将上一次推入总数据列中.
            if c_tick["short_name"].__eq__(short_name):
                self.__change_list_tick.remove(c_tick)
                return c_tick
        return None

    def get_trade_link(self,item_name):
        return f"https://www.okx.com/trade-spot/{item_name}"

#----------------------------------------------------------------------------------------

class PremiumChange(AbstractEventListener):
    def before_change_value_of(self,element, driver):
        print(element)
        print("price change!")











