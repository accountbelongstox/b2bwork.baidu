from kernel.base_class.base_class import *
import os
# import re
import urllib
import http.cookiejar
from bs4 import BeautifulSoup
# import requests
from concurrent.futures import ThreadPoolExecutor,as_completed
# from multiprocessing import Pool,Process

class HttpCommon(BaseClass):

    def __init__(self):
        pass


    def open_url_beautifulsoup(self,url,decode="utf-8"):
        content = self.open_url(url,decode)
        soup = self.beautifulsoup_wrap(content)
        return soup

    def find_text_from_beautifulsoup(self,content):
        soup = self.beautifulsoup_wrap(content)
        return soup

    def beautifulsoup_wrap(self,content):
        soup = BeautifulSoup(content, 'lxml')
        return soup


    def open_url(self,url,decode="utf-8"):
        cookie = http.cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cookie)
        header = [
            ("accept-language", "zh-CN,zh,en;q=0.9"),
            ("sec-ch-ua", "Not A;Brand\";v=\"99\", \"Chromium\";v=\"102\", \"Google Chrome\";v=\"102"),
            ("sec-ch-ua-mobile", "?0"),
            ("sec-ch-ua-platform", "Windows"),
            ("sec-fetch-dest", "empty"),
            ("sec-fetch-mode", "cors"),
            ("sec-fetch-site", "same-origin"),
            ("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36")
        ]
        opener = urllib.request.build_opener(handler)
        opener.addheaders = header
        text = opener.open(url)
        content = text.read()
        if type(decode) == str:
            content = content.decode(decode)
        return content


    def down_files(self,tupes_or_list):
        """
        多线程版
        :param tupes_or_list:
        @ 参数为 tuple 类型，则格式为 [
            ( url, file_name , override , callback),
            ( url, file_name , override , callback)
                                    ]
        @ 参数为 list 类型,则格式为[url] filename 及 override 将会自动解析
        :return:
        """
        parse_tuple = False
        urllist = []
        for simple_url in tupes_or_list:
            if type(simple_url) == str:
                parse_tuple = True
                urllist.append(
                    (
                        #url
                        simple_url,
                    )
                )
        if parse_tuple == False:
            urllist = tupes_or_list
        max_workers = 50
        if len(urllist) < max_workers:
            max_workers = len(urllist)
        if max_workers > 0:
            with ThreadPoolExecutor(max_workers=max_workers) as threadPool:
                thread_pools = []
                # threadPool.map(self.down_file,urllist)
                for urlli in urllist:
                    future = threadPool.submit(self.down_file, urlli)
                    thread_pools.append(future)
                for future in as_completed(thread_pools):
                    future.result()
        else:
            return False

    def down_file(self,url="url",file_name="",override=False,callback=None):
        """
        @ 参数 url为 tuple 类型，则格式为 [
            ( url, file_name , override),
            ( url, file_name , override)
                                        ]  后面filename 及 override 不用传
        @ 参数为 list 类型,则格式为[url] filename 及 override 将会自动解析
        :param url:
        :param file_name:
        :param override:
        :return:
        """
        if type(url) == tuple:
            urlistuple = url
            #print(urlistuple)
            url = urlistuple[0]
            if len(urlistuple) > 1:
                file_name = urlistuple[1]
            else:
                file_name = os.path.basename(url)

            if len(urlistuple) > 2:
                override = urlistuple[2]

            if len(urlistuple) > 3:
                callback = urlistuple[3]
        #str processing
        cookie = http.cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cookie)
        header = [
            ("sec-ch-ua", "Not A;Brand\";v=\"99\", \"Chromium\";v=\"102\", \"Google Chrome\";v=\"102"),
            ("sec-ch-ua-platform", "Windows"),
            ("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36")
        ]

        opener = urllib.request.build_opener(handler)
        opener.addheaders = header
        print(f"wget start [{url} to {file_name}]")
        try:
            text = opener.open(url)
            print(f"wget done {url}")
            content = text.read()
            #print("----------------------------------")
            m = "r"
            if override == False and os.path.isfile(file_name):
                return
            basename = os.path.dirname(file_name)
            # print(f"save-file ：{file_name}．")
            if os.path.exists(basename) is not True and os.path.isdir(basename) is not True:
                self.mkdir(basename)
            elif override == True:
                m = "w"
            f = open(file_name, f"{m}b+")
            f.write(content)
            f.close()
            if callback != None:
                return callback((file_name,content))
            else:
                return content
        except:
            if callback != None:
                return callback((file_name,None))
            else:
                return None

    def mkdir(self, dir):
        if os.path.exists(dir) and os.path.isdir(dir):
            return False
        else:
            os.makedirs(dir, exist_ok=True)
            return True
