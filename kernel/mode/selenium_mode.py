import shutil
from kernel.base_class.base_class import *
import os
import re
import time
#import lxml.html
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
# from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.common.exceptions import NoSuchElementException
# import sched

# 为保证 driver 能正常打开
driver = None
webdriver_ = webdriver
threadLock = threading.Lock()


class SeleniumMode(BaseClass):
    __downloadedGoogledriverHTML = False
    __down_web_resource_list = []
    __down_web_page_queue =Queue()
    __down_web_base_url = None
    __down_web_historical = set()
    __down_web_thread_pool = None
    __down_web_charset = None
    __down_web_tab_threads = []
    __down_web_driver = None
    __down_web_downing = True
    __down_web_listen_tag_init = True
    __down_web_listen_tag_flag = True

    def __init__(self):
        # self.get_googledriver_from_cmd()
        #self.get_googledriver_from_down()
        #self.__googledriver_down_and_extract("bin/chromedriver_win32-v76.0.3809.zip")
        pass

    def open_url(self,url,empty_driver=False,headless=False):
        #driver 要放外面
        global driver
        if empty_driver == True:
            print("if empty_driver == True:")
            driver = self.get_empty_driver(headless)
        else:
            if driver == None:
                driver = self.get_empty_driver(headless)
        driver.get(url)
        return driver

    def open_new_window(self,driver,url_web):
        js = "window.open('{}','_blank');"
        driver.execute_script(js.format(url_web))

    def open_local_html_to_beautifulsoup(self,html_name="index.html"):
        content = self.file_common.load_html(html_name)
        beautifulsoup = self.http_common.find_text_from_beautifulsoup(content)
        return beautifulsoup

    def get_options(self,headless=False):
        global webdriver_
        options = webdriver_.ChromeOptions()
        # 处理SSL证书错误问题
        # prefs = {'profile.managed_default_content_settings.images': 2}
        # options.add_experimental_option('prefs', prefs)
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--disable-infobars')# 禁用浏览器正在被自动化程序控制的提示
        #options.add_argument('--blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        if headless:
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
        return  options

    def get_chromedriverpath(self,version="102.0.5005.61"):
        bin_dir = self.config_common.get_bin_dir()
        chromedriver_path = None
        if self.is_windows():
            chromedriver_path = os.path.join(bin_dir , f"chromedriver_win32_v{version}.exe")
        if self.is_linux():
            chromedriver_path = os.path.join(bin_dir , f"chromedriver_linux64_v{version}")
        if os.path.exists(chromedriver_path) and os.path.isfile(chromedriver_path) :
            return chromedriver_path
        else:
            self.get_googledriver_from_down(version=version)
            return chromedriver_path

    def get_empty_driver(self,headless=False):
        global driver
        global webdriver_
        driver = None
        options = self.get_options(headless)
        driver_path = self.get_chromedriverpath()
        print(f"driver_path {driver_path}")
        driver = webdriver_.Chrome(executable_path=driver_path,chrome_options=options)
        driver.set_window_rect(x=200, y=20, width=1950, height=980)
        return driver


    async def switch_to(self,index):
        await index
        await self.__down_web_driver.switch_to.window(self.__down_web_driver.window_handles[index])
        print(dir(self.__down_web_driver.page_source))
        HTML_Content = self.__down_web_driver.page_source
        print(f"HTML_Content:{len(HTML_Content)}")

    def switch_to_window_by_url_and_open(self,driver,url):
        url_is_exist = self.switch_to_window_by_url(driver,url)
        if url_is_exist == False:
            self.open_new_window(driver,url)
            time.sleep(1)
            return driver.current_window_handle
        else:
            return url_is_exist

    def switch_to_window_by_url(self,driver,url,loop_startpoint_handle_index=None):
        current_url = driver.current_url
        # print(driver.current_window_handle.index("t"))
        if current_url.find(url) == 0:
            return driver.current_window_handle
        if loop_startpoint_handle_index != None:
            driver.switch_to.window(driver.window_handles[loop_startpoint_handle_index])
            time.sleep(1)
        current_window_handle_index = self.current_window_handle_index(driver)
        #已循环对比了一圈
        if loop_startpoint_handle_index != None and loop_startpoint_handle_index == current_window_handle_index:
            return False
        return self.switch_to_window_by_url(driver,url, (current_window_handle_index+1) )

    def current_window_handle_index(self,driver):
        current_window_handle = driver.current_window_handle
        for i in range(len(driver.window_handles)):
            if current_window_handle == driver.window_handles[i]:
                return i
        return -1

    def document_initialised(self,driver):
        outerHTML = driver.execute_script("return document.documentElement.outerHTML")
        if outerHTML != None and len(outerHTML) > 0:
            print(f"outerHTML{len(outerHTML)}")
        return driver

    def down_website_openurl_by_thread(self,url):
        PoolExecutor = ThreadPoolExecutor(max_workers = 3)
        PoolExecutor.submit(self.down_website_open,(url,))
        PoolExecutor.submit(self.down_website_foreach_tag)

    def down_website_open(self,urls):
        url = urls[0]
        driver = self.open_url(url)

    def down_website(self, web_url):
        #通过新线程启动一个浏览器
        web_url_parse = urlparse(web_url)
        down_web_base_url = web_url_parse.scheme + "://" + web_url_parse.netloc
        self.__down_web_base_url = down_web_base_url
        #首次提交的网页也先加入队列，该方便对比重复
        website_url_to_file_format = self.down_website_url_to_file_format(web_url,"<a>",None,web_url)
        url_local = website_url_to_file_format[0]
        # t = threading.Thread(target=self.down_website_openurl_by_thread,args=(url_local,),daemon=True)
        # t.run()
        self.down_website_openurl_by_thread(url_local)
        return

        self.down_website_add_webpageQueue(web_url,url_local)
        self.down_website_add_webpageQueue("https://translate.google.cn/?sl=en&tl=zh-CN&op=translate",url_local)
        self.down_website_add_webpageQueue("https://blog.csdn.net/chaodaibing/article/details/115016791",url_local)
        # self.down_website_add_to_thread()
        # max_workers = 1
        # with ThreadPoolExecutor(max_workers=max_workers) as Pool:
        #     trail_page_thread = Pool.submit(self.down_website_run)
        #     trail_page_thread.result()
        #     print("the tick.")
        max_workers = 30
        with ThreadPoolExecutor(max_workers = max_workers) as Pool:
            while self.down_website_queue_not_clear():
                #初始化执行，先监听所有TAG而，并单独使用一个线程实时切换。
                request_type = None
                if self.__down_web_listen_tag_init == True:
                    request_type = "listen_tag"
                    self.__down_web_listen_tag_init = False
                    run_parame = (request_type,None )
                elif self.__down_web_page_queue.qsize() > 0:
                    request_type = 'page_url'
                    web_page = self.__down_web_page_queue.get()
                    run_parame = (request_type,web_page )
                if request_type == "listen_tag":
                    # th = threading.Thread(target=self.down_website_open_page_on_tag,args=request_type)
                    # th.daemon = True
                    # print(th.daemon)
                    # th.start()
                    th = threading.Thread(target=self.down_website_foreach_tag)
                    th.daemon = True
                    th.start()
                elif request_type == "page_url":
                    trail_page_thread = Pool.submit(self.down_website_open_page_on_tag, run_parame)
                if request_type == 'page_url':
                    try:
                        trail_page_thread.result()
                    except:
                        print("timeout")
                        pass
                    # print("trail_page_threadtick",trail_page_thread.done())
                    pass
                    # trail_page_thread.result()
                    # print("ok!.")
                    # elif len(self.__down_web_resource_list) > 0:
                    #     pass
                    # print('self.__down_web_page_queue.qsize() ', self.__down_web_page_queue.qsize(),web_page )
                    # trail_page_thread = Pool.submit(self.down_website_open_page_on_tag,run_parame)
            # 一旦所有页面都下载完毕。
        self.__down_web_downing = False
            # trail_page_thread.result()
            # self.down_website_run()
        # 所有tab都关闭，代表没有页面了
        # 所有资源表都清空，代表下载完了
        # 所有列表面都清空，代表不开新的TAB标签了。

    def down_website_url_to_file_format(self,current_url,tag_type,ele,base_url):
        url_urlparse = urlparse(current_url)
        base_url_urlparse = urlparse(self.__down_web_base_url)
        url_path = str(url_urlparse.path)
        url_query = url_urlparse.query
        url_offset = url_path
        if self.down_website_equal_url_strict(self.__down_web_base_url,current_url) == False:
            #对于用二级域名的图片,则直接将二级域名移到当前文件夹做为目录
            url_offset = f"/{url_urlparse.netloc}{url_path}"
        if tag_type.__eq__("<script>"):
            #对于没有js地址的动态获取数据,则直接强行在最后加上.cs结尾
            if url_offset.endswith(f".js") is not True:
                url_offset = f"{url_path}{url_query}.js"
        #link文件命名规则
        elif tag_type.__eq__("<link>"):
            if (url_offset_link := self.down_website_source_link_suffix( ele,url_offset,url_path,url_query, "rel")) !=None :
                url_offset = url_offset_link
            elif (url_offset_link := self.down_website_source_link_suffix( ele,url_offset,url_path,url_query, "type")) != None:
                url_offset = url_offset_link
        #a连接文件命名规则
        elif tag_type.__eq__("<a>"):
            if self.down_website_equal_url(self.__down_web_base_url, current_url) is not True:
                return None
            filename_split = os.path.splitext(url_offset)
            if filename_split[1].__eq__(""):
                url_offset = f"{url_offset}/index.html"
        url_offset = re.sub(r"[\=\|\?\^\*\`\;\,\，\&]","_",url_offset)
        #filename Format
        filename_url = self.down_website_url_format(
            f"{base_url_urlparse.netloc}/{url_offset}"
        )
        url_local = self.down_website_url_format(
            self.down_website_url_to_localdir(filename_url)
        )
        url_offset = self.down_website_join_path(base_url, url_offset)
        return (url_local,url_offset)


    def down_website_foreach_tag(self):
        print("down_website_foreach_tag")
        index = 0
        while True:
            tab_threads_ok = len(self.__down_web_tab_threads) > 0
            # print("listening ：while",(self.__down_web_driver != None and tab_threads_ok > 0))
            if self.__down_web_driver != None and tab_threads_ok > 0:
                if index == len(self.__down_web_driver.window_handles):
                    index = 0
                print("index",index)
                self.__down_web_driver.switch_to.window(self.__down_web_driver.window_handles[index])

                # WebDriverWait(self.__down_web_driver, timeout=1).until(
                #     EC.presence_of_element_located( (By.TAG_NAME,"html") ))
                WebDriverWait(self.__down_web_driver, timeout=1).until(EC.visibility_of( driver.find_element(By.TAG_NAME, "html") ))
                try:
                    WebDriverWait(self.__down_web_driver, timeout=1).until(EC.any_of((By.TAG_NAME,"html")))
                    outerHTML = self.__down_web_driver.execute_async_script("return document.documentElement.outerHTML")
                    print("outerHTML",len(outerHTML))
                except:
                    print("time out.")
                    print(dir(EC))
                # self.__down_web_driver.set_script_timeout(1)
                # file_detector_context = self.__down_web_driver.title
                # print("file_detector_context",file_detector_context)
                index += 1
#                 outerHTML = self.__down_web_driver.execute_script("""
#                 var _doc = null;
# fn = ()=>{
# 	if (document){
# 	_doc  = document;
# 	}
# }
# setInterval(fn,1000);""")
                # with ThreadPoolExecutor(max_workers=10) as p:
                #     p.submit(self.switch_to,index)
                #     index += 1
                # th = threading.Thread(target=self.switch_to,args=[index])
                # index += 1
                # th.daemon = False
                # th.start()
                # th.join(timeout=1)
            else:
                pass
                # print("loading driver and the property switch_to!")

    def down_website_foreach_tag_test(self):
        print("listening ：while")
        while True:
            print("self.__down_web_downing", self.__down_web_downing)


    async def down_website_open_page_on_tag_async(self):
        url_web ="http://www.google.com"
        threadLock.acquire()
        web_tab_threads = len(self.__down_web_tab_threads)
        if web_tab_threads < 1 or self.__down_web_driver == None:
            self.__down_web_driver = self.get_empty_driver()
            # self.__down_web_driver.set_script_timeout(1)
            # self.__down_web_driver.set_page_load_timeout(3)
            threadLock.release()
            self.open_url(url_web)
        else:
            js = "window.open('{}','_blank');"
            threadLock.release()
            self.__down_web_driver.execute_script(js.format(url_web))
        #--线程安全==
        index = self.down_website_get_webtab_index(url_web)
        # self.down_website_foreach_tag()
        self.__down_web_tab_threads.append(url_web)
        if self.__down_web_listen_tag_flag:
            self.__down_web_listen_tag_flag = False
        #===========
        print("exec ok.",index)

        yield 1
    #两个线程池，一个专用于打开页面，用于等待页面加载完成,
    #另一个用于专门下载资源，也可两个线程同时调用，其中的资源文件直接下载，html和css则提取其中内容。
    def down_website_open_page_on_tag(self,run_param):
        request_type = run_param[0]
        if request_type == "page_url":
            web_page = run_param[1]
            # print("self.__down_web_page_queue.qsize()",self.__down_web_page_queue.qsize())
            url_web = web_page[0]
            url_local = web_page[1]

            threadLock.acquire()
            web_tab_threads = len(self.__down_web_tab_threads)

            if web_tab_threads < 1 or self.__down_web_driver == None:
                self.__down_web_driver = self.get_empty_driver(headless=False)
                # self.__down_web_driver.set_script_timeout(1)
                # self.__down_web_driver.set_page_load_timeout(3)
                threadLock.release()
                self.open_url(url_web)
            else:
                js = """return window.open('{}','_blank');"""
                threadLock.release()
                self.__down_web_driver.execute_script(js.format(url_web))

            index = self.down_website_get_webtab_index(url_web)
            # self.down_website_foreach_tag()
            self.__down_web_tab_threads.append(url_web)
            if self.__down_web_listen_tag_flag:
                self.__down_web_listen_tag_flag = False
            #===========
            print("exec ok.",index)

    def down_website_queue_not_clear(self):
        if len(self.__down_web_tab_threads) > 0 \
            or \
            self.__down_web_page_queue.qsize() > 0 \
            or \
            len(self.__down_web_resource_list) > 0:
            return True
        else:
            return False

    def down_website_source_thread(self):
        th = []
        while len(self.__down_web_resource_list) >0:
            th.append(self.__down_web_resource_list.pop())
        if len(th) == 0:
            return
        return self.http_common.down_files(th)

    def down_website_run(self):
        while self.down_website_continue():
            while self.__down_web_page_queue.qsize() > 0:
                web_page = self.__down_web_page_queue.get()
                url_web = web_page[0]
                url_local = web_page[1]
                if len(self.__down_web_tab_threads) < 1:
                    driver = self.open_url(url_web)
                else:
                    js = "window.open('{}','_blank');"
                    driver.execute_script(js.format(url_web))
                self.__down_web_tab_threads.append(url_web)
                HTML_Content = driver.page_source
                _bdriver = self.http_common.find_text_from_beautifulsoup(HTML_Content)
                self.down_website_set_chatset( _bdriver)
                HTML_Content = self.down_website_find_source_add_toQueue(_bdriver, url_web,HTML_Content, "<script>", "src")
                HTML_Content = self.down_website_find_source_add_toQueue(_bdriver, url_web,HTML_Content, "<img>", "src")
                HTML_Content = self.down_website_find_source_add_toQueue(_bdriver, url_web,HTML_Content, "<link>", "href")
                HTML_Content = self.down_website_find_a_add_toQueue(_bdriver, url_web,HTML_Content, "<a>", "href")

                self.file_common.save_file(url_local,HTML_Content,override=True,encoding=self.__down_web_charset)
                print(f"tick done-{url_web}:historical:{len(self.__down_web_historical)}")

                th = []
                while len(self.__down_web_resource_list) > 0:
                    th.append(self.__down_web_resource_list.pop())
                if len(th) != 0:
                    self.http_common.down_files(th)


    def down_website_get_webtab_index(self,web_url):
        threadLock.acquire()
        for id,url in enumerate(self.__down_web_tab_threads):
            if url.__eq__(web_url):
                threadLock.release()
                return id
        threadLock.release()
        return None


    def down_website_run_backup(self):
        while self.__down_web_page_queue.qsize() > 0 or self.__down_web_page_queue.qsize() > 0:
            while self.__down_web_page_queue.qsize() > 0:
                web_page = self.__down_web_page_queue.get()
                url_web = web_page[0]
                url_local = web_page[1]
                driver = self.open_url(url_web)

                HTML_Content = driver.page_source
                self.down_website_set_chatset( driver)
                HTML_Content = self.down_website_find_source_add_toQueue(driver, url_web,HTML_Content, "<script>", "src")
                HTML_Content = self.down_website_find_source_add_toQueue(driver, url_web,HTML_Content, "<img>", "src")
                HTML_Content = self.down_website_find_source_add_toQueue(driver, url_web,HTML_Content, "<link>", "href")
                HTML_Content = self.down_website_find_a_add_toQueue(driver, url_web,HTML_Content, "<a>", "href")

                self.file_common.save_file(url_local,HTML_Content,override=True,encoding=self.__down_web_charset)
                print(f"tick done-{url_web}:historical:{len(self.__down_web_historical)}")

                th = []
                while len(self.__down_web_resource_list) > 0:
                    th.append(self.__down_web_resource_list.pop())
                if len(th) != 0:
                    self.http_common.down_files(th)

    def down_website_join_path(self,base_url,current_dir):
        base_url_parse = urlparse(base_url)
        base_url_path = base_url_parse.path
        current_url_parse = urlparse(current_dir)
        current_url_path = current_url_parse.path
        base_url_path = self.down_website_url_format(base_url_path)
        current_url_path = self.down_website_url_format(current_url_path)
        if current_url_path.startswith("/"):
            current_url_path_dirname = os.path.dirname(current_url_path)
            base_url_paths = self.down_website_url_split(base_url_path)
            current_url_paths = self.down_website_url_split(current_url_path)
            # 先将相同的路径深度依次递归向上抵消相同路径
            while True:
                if len(base_url_paths) < 1 or len(current_url_paths) < 1:
                    break
                if base_url_paths[0].__eq__(current_url_paths[0]):
                    base_url_paths = base_url_paths[1:]
                    current_url_paths = current_url_paths[1:]
                else:
                    break
            if len(current_url_paths) > 0:
                current_url_path = "/".join(current_url_paths)
            else:
                current_url_path = ""
            #先检查两个路径是否相等
            if base_url_path.__eq__(current_url_path_dirname):
                #如果路径相等则先把路径替换为相对路径,直接抵消可以不用替换为相对路径，直接返回即可。
                current_url_path = re.sub(re.compile(r"^\/"),"",current_url_path)
            #对于不相等的路径，则要由当前页面的深度依次递归向上返回主路径再找到相对路径
            else:
                current_url_path = "../" * len(base_url_paths) + "/".join(current_url_paths)
        return current_url_path

    def down_website_set_chatset(self,driver):
        if self.__down_web_charset == None:
            metas = self.find_elements(driver, "<meta>")
            for meta in metas:
                charset = meta.get_attribute("charset")
                if charset != None:
                    self.__down_web_charset = charset
                    break
        if self.__down_web_charset == None:
            self.__down_web_charset = "utf-8"

    def down_website_is_historical_url(self,url):
        threadLock.acquire()
        if url in self.__down_web_historical:
            threadLock.release()
            return True
        else:
            self.__down_web_historical.update(url)
            threadLock.release()
            return False

    def down_website_url_to_localdir(self,web_url):
        url_parse = urlparse(web_url)
        webdownload_dir = self.config_common.get_webdownload_dir()
        baseDir = os.path.join(webdownload_dir, url_parse.netloc)
        url_parse_path = re.sub(re.compile(r"^\/"),"",url_parse.path)
        fod_dir = os.path.join(baseDir, url_parse_path)
        return fod_dir

    def down_website_find_a_add_toQueue(self,driver,url_web,HTML_Content,tagname,atr):
        HTML_Content = self.down_website_find_add_toQueue(driver,url_web,HTML_Content,tagname,atr,is_alink=True)
        return HTML_Content
    def down_website_find_source_add_toQueue(self,driver,url_web,HTML_Content,tagname,atr):
        HTML_Content = self.down_website_find_add_toQueue(driver,url_web,HTML_Content,tagname,atr,is_alink=False)
        return HTML_Content
    def down_website_find_add_toQueue(self,driver,url_web,HTML_Content,tagname,atr,is_alink=False):
        tags = self.find_elements(driver, tagname)
        for ele in tags:
            attribute = ele.get_attribute(atr)
            dom_attribute = ele.get_dom_attribute(atr)
            if attribute == None:
                continue
                #javascript 空标签跳过
            if attribute.startswith("javascript:"):
                continue
            if dom_attribute == None:
                continue
            if dom_attribute.startswith("javascript:"):
                continue

            attribute = str(attribute)
            attribute = attribute.strip()
            dom_attribute = str(dom_attribute)
            dom_attribute = dom_attribute.strip()
            if attribute.__eq__(""):
                continue
            if dom_attribute.__eq__(""):
                continue
                #空字符串及当前而跳过
            if attribute.__eq__("/"):
                continue
            if dom_attribute.__eq__("/"):
                continue
            #对于已经存在的历史url跳过
            if self.down_website_is_historical_url(attribute) == True:
                print(f"already down the url:<{attribute}>")
                continue
            if self.down_website_is_historical_url(url_web) == True:
                print(f"already down the url:<{url_web}>")
                continue

            urls_format_and_locat = self.down_website_url_to_file_format(attribute,tagname,ele,url_web)
            if urls_format_and_locat == None:
                continue
            url_offset = urls_format_and_locat[1]
            url_local = urls_format_and_locat[0]
            if is_alink:
                self.down_website_add_webpageQueue(attribute, url_local)
            else:
                HTML_Content = self.down_website_replace_htmlcontent(HTML_Content, dom_attribute, url_offset)
                self.down_website_add_resourceList(attribute, url_local)
        return HTML_Content

    def down_website_equal_url(self,url_main,url_other):
        url_main_parse = urlparse( url_main )
        url_main = url_main_parse.netloc
        url_main = re.sub( re.compile(r"^www\."), "", url_main )
        url_other_parse = urlparse( url_other )
        url_other = url_other_parse.netloc
        url_other = re.sub( re.compile(r"^www\."), "", url_other )
        if url_other.endswith(url_main) or url_main.endswith( url_other ):
            return True
        else:
            return False

    def down_website_equal_url_strict(self,url_main,url_other):
        url_main_parse = urlparse( url_main )
        url_main = url_main_parse.netloc.lower()
        url_other_parse = urlparse( url_other )
        url_other = url_other_parse.netloc.lower()
        if url_main.__eq__(url_other):
            return True
        else:
            return False

    def down_website_replace_htmlcontent(self, HTML_Content,dom_attribute,url_to_file_format):
        dom_attribute_s = dom_attribute
        dom_attribute_t = url_to_file_format
        # dom_attribute_s = f'="{dom_attribute}'
        # dom_attribute_t = f'="{url_to_file_format}'
        # HTML_Content = HTML_Content.replace(dom_attribute_s, dom_attribute_t)
        # dom_attribute_s = f"='{dom_attribute}"
        # dom_attribute_t = f"='{url_to_file_format}"
        # HTML_Content = HTML_Content.replace(dom_attribute_s, dom_attribute_t)
        # dom_attribute_s = f"={dom_attribute}"
        # dom_attribute_t = f"={url_to_file_format}"
        HTML_Content = HTML_Content.replace(dom_attribute_s, dom_attribute_t)
        return  HTML_Content

    def down_website_source_link_suffix(self,ele,url_offset,url_path,url_query,link_attr):
        # 根据link的类型查找对应后续名字。
        url_NewOffset = None
        taty = ele.get_attribute(link_attr)
        taty = str(taty).strip()
        taties = re.split(re.compile(r"\s+"), taty)
        taties = [tag.lower() for tag in taties]
        down_classic = {
            "rel": [
                ("icon", "icon"),
                ("preload", None),
                ("stylesheet", "css"),
                ("mask-icon", "icon"),
                ("fluid-icon", "icon"),
                ("search", None)
            ],
            "type": [
                ("text/css", "css"),
                ("text/javascript", "js"),
            ]
        }
        down_refs = down_classic[link_attr]
        fetch_property = [t[0] for t in down_refs]
        intersection = set(taties).intersection(fetch_property)
        if len(intersection) > 0:
            reftype = intersection.pop()
            for ref in down_refs:
                refname = ref[0]
                suffix = ref[1]
                if suffix != None and refname.__eq__(reftype) and url_offset.endswith(f".{suffix}") is not True:
                    url_NewOffset = f"{url_path}{url_query}.{suffix}"
                    break
        return url_NewOffset

    def down_website_url_format(self,url):
        url = re.sub(re.compile(r"[\/\\]+"), "/", url)
        return url

    def down_website_url_split(self,url):
        urls = [ p.strip() for p in re.split( re.compile(r"[\/]+"), url) if p != "" ]
        return urls

    def down_website_add_webpageQueue(self,url_web,url_local):
        self.__down_web_page_queue.put(
            (url_web, url_local)
        )

    def down_website_add_resourceList(self,url_web,url_local):
        threadLock.acquire()
        self.__down_web_resource_list.append(
            (url_web, url_local,True)
        )
        threadLock.release()

    def down_website_get_resourceList(self):
        threadLock.acquire()
        web_resource_item = self.__down_web_resource_list.pop()
        threadLock.release()
        return web_resource_item

    def find_element(self,driver,selector):
        eles = self.find_elements(driver,selector)
        ele = None
        if len(eles) > 0:
            ele = eles[0]
        return ele

    def is_beautifulsoup(self,driver):
        if driver.__class__.__name__.__eq__("BeautifulSoup"):
            return True
        else:
            return False

    def find_element_wait(self,driver,selector):
        print(f"find_element_wait {selector}")
        try:
            ele = self.find_element(driver,selector)
            if ele != None:
                return ele
            raise NoSuchElementException
        except:
            time.sleep(0.5)
            return self.find_element_wait(driver,selector)

    def find_elements_value_wait(self,driver,selector):
        print(f"find_elements_value_wait {selector}")
        ele = self.find_element_wait(driver,selector)
        try:
            text = ele.text
            text = text.replace("0","")
            if len(text) > 0:
                return ele.text
            raise NoSuchElementException
        except:
            time.sleep(0.5)
            return self.find_elements_value_wait(driver,selector)
        # texts = []
        # for el in range(cont):
        #     js = f"return document.querySelectorAll('{selector}')[{el}].textContent"
        #     text = self.execute_javascript_wait(driver,js)
        #     texts.append(text)
        #     print(text)
        # return texts


    def find_elements(self,driver,selector):
        st = self.parse_selector(selector)
        is_beautifulsoup = self.is_beautifulsoup( driver)
        if st == "css":
            ele = self.elementsBy_CSS(driver,selector,is_beautifulsoup)
        elif st == "xpath":
            ele = self.elementsBy_XPATH(driver,selector,is_beautifulsoup)
        if st == "id":
            ele = self.elementsBy_ID(driver,selector,is_beautifulsoup)
        if st == "tag":
            ele = self.elementsBy_TAGNAME(driver,selector,is_beautifulsoup)
        if type(ele) != list:
            eles = [ele]
        else:
            eles = ele
        return eles

    def find_element_value_by_js_wait(self,driver,selector):
        if selector[0] == '/':
            js = f"return document.evaluate('{selector}',document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null,).singleNodeValue.innerHTML"
        else:
            js = f"return document.querySelector('{selector}').textContent"
        return self.execute_javascript_wait(driver,js)

    def find_elements_value_by_js_wait(self,driver,selector):
        cont = self.find_elements_count_wait(driver,selector)
        cont = int(cont)
        texts = []
        for el in range(cont):
            js = f"return document.querySelectorAll('{selector}')[{el}].textContent"
            text = self.execute_javascript_wait(driver,js)
            texts.append(text)
        return texts

    def find_elements_count_wait(self,driver,selector):
        js = f"return document.querySelectorAll('{selector}').length.toString()"
        cont = self.execute_javascript_wait(driver,js)
        cont = int(cont)
        if cont > 0:
            print(f"find_elements_count_wait cont:{cont}")
            return cont
        else:
            time.sleep(1)
            print(f"find_elements_count_wait retrying cont:{cont}")
            return self.find_elements_count_wait(driver,selector)

    def second_find_elements(self,ele,selector):
        st = self.parse_selector(selector)
        print(f"second_find_elements {selector}")
        eles = None
        if st == "css":
            eles = ele.find_elements(By.CSS_SELECTOR,selector)
        if st == "xpath":
            eles = ele.find_element(By.XPATH,selector)
        if st == "id":
            selector = selector[1:]
            eles = ele.find_element(By.ID,selector)
        if st == "tag":
            eles = ele.find_elements(By.TAG_NAME, selector.replace("<","").replace(">",""))
        if st == "text":
            eles = ele.find_elements_by_link_text(selector)
        return eles

    def parse_selector(self, selector):

        HTML_TABS = ["<a>", "<abbr>", "<acronym>", "<abbr>", "<address>", "<applet>", "<embed>", "<object>", "<area>",
                     "<article>", "<aside>", "<audio>", "<b>", "<base>", "<basefont>", "<bdi>", "<bdo>", "<big>",
                     "<blockquote>", "<body>", "<br>", "<button>", "<canvas>", "<caption>", "<center>", "<cite>",
                     "<code>", "<col>", "<colgroup>", "<command>", "<data>", "<datalist>", "<dd>", "<del>", "<details>",
                     "<dir>", "<div>", "<dfn>", "<dialog>", "<dl>", "<dt>", "<em>", "<embed>", "<fieldset>",
                     "<figcaption>", "<figure>", "<font>", "<footer>", "<form>", "<frame>", "<frameset>", "<h1>",
                     "<h2>", "<h3>", "<h4>", "<h5>", "<h6>", "<head>", "<header>", "<hr>", "<html>", "<i>", "<iframe>",
                     "<img>", "<input>", "<ins>", "<isindex>", "<kbd>", "<keygen>", "<label>", "<legend>", "<li>",
                     "<link>", "<main>", "<map>", "<mark>", "<menu>", "<menuitem>", "<meta>", "<meter>", "<nav>",
                     "<noframes>", "<noscript>", "<object>", "<ol>", "<optgroup>", "<option>", "<output>", "<p>",
                     "<param>", "<pre>", "<progress>", "<q>", "<rp>", "<rt>", "<ruby>", "<s>", "<samp>", "<script>",
                     "<section>", "<select>", "<small>", "<source>", "<span>", "<strike>", "<del>", "<s>", "<strong>",
                     "<style>", "<sub>", "<summary>", "<details>", "<sup>", "<svg>", "<table>", "<tbody>", "<td>",
                     "<template>", "<textarea>", "<tfoot>", "<th>", "<thead>", "<time>", "<title>", "<tr>", "<track>",
                     "<tt>", "<u>", "<ul>", "<var>", "<video>", "<wbr>", "<xmp>"]
        if selector[0] == ".":
            return "css"
        elif selector[0] == "/":
            return "xpath"
        if selector[0] == "#":
            return "id"
        if selector.strip().lower() in HTML_TABS:
            return "tag"
        return "text"

    def elementsBy_TAGNAME(self,driver,selector,is_beautifulsoup):
        if is_beautifulsoup:
            eles = driver.find_all(selector)
        else:
            eles = driver.find_elements_by_link_text(selector)
        return eles


    def elementsBy_ID(self,driver,selector,is_beautifulsoup):
        selector = selector[1:]
        if is_beautifulsoup:
            ele = [ driver.find(id=selector) ]
        else:
            ele = [ driver.find_element(By.ID, selector) ]
        return ele

    def elementsBy_CSS(self,driver,selector,is_beautifulsoup):
        eles = []
        if is_beautifulsoup:
            html = str(driver.html)
            tree = etree.HTML(html)
            selector = CSSSelector(selector)
            for ele in selector(tree):
                eles.append(ele)
        else:
            eles = driver.find_elements(By.CSS_SELECTOR,selector)
        return eles


    def elementsBy_XPATH(self,driver,selector,is_beautifulsoup):
        if is_beautifulsoup:
            html = str(driver.html)
            tree = etree.HTML(html)
            ele = tree.xpath("//*")
        else:
            print(f"elementsBy_XPATH element ",selector)
            ele = driver.find_element(By.XPATH, selector)
        return ele

    def find_text_from(self,driver, selector, s_text):
        menus = self.find_elements(driver, selector)
        index = 0
        eles = []
        for m in menus:
            text = m.text
            if text == None:
                text = ""
            text = text.strip()
            if text.__eq__(s_text):
                eles.append(menus[index])
            index += 1
        return eles[0]

    def wait_element_and_paurse(self,driver,selector):
        st = self.parse_selector(selector)
        if st == "css":
            WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        elif st == "xpath":
            pass
        if st == "id":
            pass
        if st == "tag":
            WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))


    def execute_js(self,driver,js):
        js_path = self.config_common.get_static("js_dir")
        js_path = os.path.join(js_path,js)
        if os.path.isfile(js_path):
            description = "isfile"
            js_string = self.file_common.load_file(js_path)
        else:
            description = "is javascript string"
            js_string = js
        print(f"execute_js js {description} {js_string[:50]}")
        return driver.execute_script(js_string)

    def execute_javascript_wait(self,driver,js):
        print(f"execute_javascript_wait of execute_js")
        try:
            return self.execute_js(driver,js)
        except:
            time.sleep(1)
            return self.execute_javascript_wait(driver,js)

    def load_JQuery(self,driver):
        print(f"load_JQuery")
        return self.execute_js(driver,"load_jquery.js")

    def load_JQuery_wait(self,driver):
        print(f"load_JQuery_wait")
        try:
            jQueryString = driver.execute_script(f"return jQuery.toString()")
            print(jQueryString)
            return True
        except:
            time.sleep(1)
            self.load_JQuery(driver)
            return self.load_JQuery_wait(driver)

    def js_find_attr(self, driver, selector, attr):
        find_element_js = f"""src___ =  $("{selector}").attr("{attr}");return src___;"""
        print(find_element_js)
        return driver.execute_script(find_element_js)

    def send_keys(self,driver,selector,val):
        driver.execute_script(f"""
        $("{selector}").val("{val}")
        """)

    def get_googledriver_versions(self):
        if self.__downloadedGoogledriverHTML != False:
            return self.__downloadedGoogledriverHTML
        document = self.http_common.open_url("https://chromedriver.storage.googleapis.com/?delimiter=/&prefix=",decode="utf-8")
        doc = self.xml_common.from_string(document)
        nodes = self.xml_common.find_all(doc,"Prefix")
        self.__downloadedGoogledriverHTML = [node.replace(r"/",'') for node in nodes if not node.startswith('icons')]
        return self.__downloadedGoogledriverHTML

    def get_googledriver_downloadurl(self,version="103.0.5060.24"):
        if self.is_windows():
            googledriver_downloadurl = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_win32.zip"
        if self.is_linux():
            googledriver_downloadurl = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_linux64.zip"
        return googledriver_downloadurl

    def get_googledriver_savename(self,version,suffix="zip"):
        googledriver_savename = f"chromedriver_win32_v{version}.{suffix}"
        return googledriver_savename


    def get_googledriver_from_down(self,version=None):
        download_tuple_urls = []
        versions = self.get_googledriver_versions()
        bin_dir = self.config_common.get_bin_dir()
        for v in versions:
            savename = os.path.join(bin_dir,self.get_googledriver_savename(v,"zip"))
            di = (
                    self.get_googledriver_downloadurl(v),
                    savename,
                    True,
                    self.googledriver_down_and_extract__
                )
            if version == None:
                download_tuple_urls.append(di)
            elif v == version:
                download_tuple_urls.append(di)
        self.http_common.down_files( download_tuple_urls)

    def googledriver_down_and_extract__(self,res):
        """
        #输助函数,将最后下载的文件解压和删除。
        :param filename:
        :return:
        """
        filename = res[0]
        extract_dir = os.path.splitext(filename)[0]
        self.file_common.zip_extractall(filename,extract_dir)
        if self.is_windows():
            old_name = os.path.join(extract_dir,"chromedriver.exe")
        if self.is_linux():
            old_name = os.path.join(extract_dir,"chromedriver")
        if self.is_windows():
            new_name = f"{os.path.splitext(filename)[0]}.exe"
        if self.is_linux():
            new_name = f"{os.path.splitext(filename)[0]}"
        shutil.copyfile(old_name,new_name)
        print(f"rmtree : {old_name}")
        shutil.rmtree(extract_dir)
        print(f"remove : {filename}")
        os.remove(filename)



    def get_googledriver_from_cmd(self):
        versions = self.get_googledriver_versions()
        cmd = ""
        bin_dir = self.config_common.get_bin_dir().replace('\\','/')
        for version in versions:
            zip_filename = self.get_googledriver_savename(version,"zip")
            exe_filename = self.get_googledriver_savename(version,"exe")
            save_file_name = f"{zip_filename}"
            url = self.get_googledriver_downloadurl(version)
            cmd += f"""wget -c {url} -O {save_file_name}
7z.exe x {save_file_name} -o"."
timeout /t 1
ren chromedriver.exe {exe_filename}
del {save_file_name}
timeout /t 1
\n"""
        cmd+="cmd"
        print(cmd)
        cmd_file = f"{bin_dir}/getchromedrivers.bat"
        print(f"cmd save to {cmd_file}")
        self.file_common.save_file(cmd_file,cmd,encoding="utf-8",override=True)


    def is_windows(self):
        import platform
        sysstr = platform.system()
        windows = "windows"
        linux = "linux"
        if (sysstr.lower() == windows):
            return True
        elif (sysstr.lower() == linux):
            return False
        return False

    def is_linux(self):
        import platform
        sysstr = platform.system()
        windows = "windows"
        linux = "linux"
        if (sysstr.lower() == windows):
            return False
        elif (sysstr.lower() == linux):
            return True
        return False