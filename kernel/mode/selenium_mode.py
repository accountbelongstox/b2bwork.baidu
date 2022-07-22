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
# from queue import Queue
# from multiprocessing import Pool
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
from selenium.common.exceptions import NoSuchElementException
# import sched
import platform
# 为保证 driver 能正常打开
from kernel.base_class.load_module_class import LoadModuleClass

drivers_dict = {}
driver = None
webdriver_as = webdriver


class SeleniumMode(BaseClass):
    __driver = None

    def __init__(self,args):
        if len(args) == 0:
            return
        driver_name_from_modulename = args[0]
        try:
            headless = args[1]
        except:
            headless = False
        LoadModuleClass().add_module(self)
        drivers_dict[driver_name_from_modulename] = self.get_empty_driver(headless=headless)
        self.__driver = drivers_dict[driver_name_from_modulename]
        pass

    # 创建一个浏览器，并可直接使用类的功能无须传递driver对象
    def main(self,args,self_mode_name=None,callback_module_name=None,headless=False):
        if type(args) == dict:
            module = args["module"]
        else:
            module = args
        if self_mode_name is None:
            self_mode_name = os.path.splitext(os.path.basename(__file__))[0]
        if callback_module_name is None:
            callback_module_name = module.__class__.__name__
        selenium_mode = SeleniumMode((callback_module_name,headless))
        module.__setattr__(self_mode_name,selenium_mode)
        module.__setattr__("__driver",selenium_mode.get_driver())

    def get_driver(self,):
        return self.__driver

    def open_url(self,url):
        self.__driver.get(url)

    def open_new_window(self,url_web):
        js = "window.open('{}','_blank');"
        self.__driver.execute_script(js.format(url_web))

    def open_local_html_to_beautifulsoup(self,html_name="index.html"):
        content = self.file_common.load_html(html_name)
        beautifulsoup = self.http_common.find_text_from_beautifulsoup(content)
        return beautifulsoup

    def get_chromedriverpath(self,version="102.0.5005.61"):
        bin_dir = self.config_common.get_bin_dir()
        if self.is_windows():
            chromedriver_path = os.path.join(bin_dir , f"chromedriver_win32_v{version}.exe")
        else:
            chromedriver_path = os.path.join(bin_dir , f"chromedriver_linux64_v{version}")
        if os.path.exists(chromedriver_path) and os.path.isfile(chromedriver_path) :
            return chromedriver_path
        else:
            self.get_googledriver_from_down(version=version)
            return chromedriver_path

    def get_empty_driver(self,headless=False):
        global driver
        global webdriver_as

        driver = None
        options = webdriver_as.ChromeOptions()
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


        driver_path = self.get_chromedriverpath()
        print(f"driver_path {driver_path}")
        driver = webdriver_as.Chrome(executable_path=driver_path,chrome_options=options)
        driver.set_window_rect(x=200, y=20, width=1950, height=980)
        return driver


    async def switch_to(self,index):
        await index
        await self.__down_web_driver.switch_to.window(self.__down_web_driver.window_handles[index])
        print(dir(self.__down_web_driver.page_source))
        HTML_Content = self.__down_web_driver.page_source
        print(f"HTML_Content:{len(HTML_Content)}")

    def switch_to_window_by_url_and_open(self,url):
        url_is_exist = self.switch_to_window_by_url(url)
        if url_is_exist == False:
            self.open_new_window(url)
            time.sleep(1)
            return self.__driver.current_window_handle
        else:
            return url_is_exist

    def switch_to_window_by_url(self,url,loop_startpoint_handle_index=None):
        driver = self.__driver
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
        return self.switch_to_window_by_url(url, (current_window_handle_index+1) )

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


    def find_element(self,selector):
        eles = self.find_elements(selector)
        ele = None
        if len(eles) > 0:
            ele = eles[0]
        return ele

    def is_beautifulsoup(self,driver):
        if driver.__class__.__name__.__eq__("BeautifulSoup"):
            return True
        else:
            return False

    def find_element_wait(self,selector):
        print(f"find_element_wait {selector}")
        try:
            ele = self.find_element(selector)
            if ele != None:
                return ele
            raise NoSuchElementException
        except:
            time.sleep(0.5)
            return self.find_element_wait(selector)

    def find_elements_value_wait(self,selector):
        print(f"find_elements_value_wait {selector}")
        ele = self.find_element_wait(selector)
        try:
            text = ele.text
            text = text.replace("0","")
            if len(text) > 0:
                return ele.text
            raise NoSuchElementException
        except:
            time.sleep(0.5)
            return self.find_elements_value_wait(selector)
        # texts = []
        # for el in range(cont):
        #     js = f"return document.querySelectorAll('{selector}')[{el}].textContent"
        #     text = self.execute_javascript_wait(driver,js)
        #     texts.append(text)
        #     print(text)
        # return texts


    def find_elements(self,selector):
        st = self.parse_selector(selector)
        is_beautifulsoup = self.is_beautifulsoup( driver)
        if st == "css":
            ele = self.elementsBy_CSS(selector,is_beautifulsoup)
        elif st == "xpath":
            ele = self.elementsBy_XPATH(selector,is_beautifulsoup)
        if st == "id":
            ele = self.elementsBy_ID(selector,is_beautifulsoup)
        if st == "tag":
            ele = self.elementsBy_TAGNAME(selector,is_beautifulsoup)
        if type(ele) != list:
            eles = [ele]
        else:
            eles = ele
        return eles

    def find_element_value_by_js_wait(self,selector):
        if selector[0] == '/':
            js = f"return document.evaluate('{selector}',document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null,).singleNodeValue.innerHTML"
        else:
            js = f"return document.querySelector('{selector}').textContent"
        return self.execute_javascript_wait(js)

    def find_elements_value_by_js_wait(self,selector):
        cont = self.find_elements_count_wait(selector)
        cont = int(cont)
        texts = []
        for el in range(cont):
            js = f"return document.querySelectorAll('{selector}')[{el}].textContent"
            text = self.execute_javascript_wait(js)
            texts.append(text)
        return texts

    def find_elements_count_wait(self,selector):
        js = f"return document.querySelectorAll('{selector}').length.toString()"
        cont = self.execute_javascript_wait(js)
        cont = int(cont)
        if cont > 0:
            print(f"find_elements_count_wait cont:{cont}")
            return cont
        else:
            time.sleep(1)
            print(f"find_elements_count_wait retrying cont:{cont}")
            return self.find_elements_count_wait(selector)

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

    def elementsBy_TAGNAME(self,selector,is_beautifulsoup):
        if is_beautifulsoup:
            eles = self.__driver.find_all(selector)
        else:
            eles = self.__driver.find_elements_by_link_text(selector)
        return eles


    def elementsBy_ID(self,selector,is_beautifulsoup):
        selector = selector[1:]
        if is_beautifulsoup:
            ele = [ self.__driver.find(id=selector) ]
        else:
            ele = [ self.__driver.find_element(By.ID, selector) ]
        return ele

    def elementsBy_CSS(self,selector,is_beautifulsoup):
        eles = []
        if is_beautifulsoup:
            html = str(self.__driver.html)
            tree = etree.HTML(html)
            selector = CSSSelector(selector)
            for ele in selector(tree):
                eles.append(ele)
        else:
            eles = self.__driver.find_elements(By.CSS_SELECTOR,selector)
        return eles


    def elementsBy_XPATH(self,selector,is_beautifulsoup):
        if is_beautifulsoup:
            html = str(self.__driver.html)
            tree = etree.HTML(html)
            ele = tree.xpath("//*")
        else:
            print(f"elementsBy_XPATH element ",selector)
            ele = self.__driver.find_element(By.XPATH, selector)
        return ele

    def find_text_from(self, selector, s_text):
        menus = self.find_elements( selector)
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

    def wait_element_and_paurse(self,selector):
        st = self.parse_selector(selector)
        if st == "css":
            WebDriverWait(self.__driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        elif st == "xpath":
            pass
        if st == "id":
            pass
        if st == "tag":
            WebDriverWait(self.__driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))


    def execute_js(self,js):
        js_path = self.config_common.get_static("js_dir")
        js_path = os.path.join(js_path,js)
        if os.path.isfile(js_path):
            description = "isfile"
            js_string = self.file_common.load_file(js_path)
        else:
            description = "is javascript string"
            js_string = js
        print(f"execute_js js {description} {js_string[:50]}")
        return self.__driver.execute_script(js_string)

    def execute_javascript_wait(self,js):
        print(f"execute_javascript_wait of execute_js")
        try:
            return self.execute_js(js)
        except:
            time.sleep(1)
            return self.execute_javascript_wait(js)

    def load_JQuery(self):
        print(f"load_JQuery")
        return self.execute_js("load_jquery.js")

    def load_JQuery_wait(self):
        print(f"load_JQuery_wait")
        try:
            jQueryString = self.__driver.execute_script(f"return jQuery.toString()")
            print(jQueryString)
            return True
        except:
            time.sleep(1)
            self.load_JQuery()
            return self.load_JQuery_wait()

    def js_find_attr(self, selector, attr):
        find_element_js = f"""src___ =  $("{selector}").attr("{attr}");return src___;"""
        print(find_element_js)
        return self.__driver.execute_script(find_element_js)

    def send_keys(self,selector,val):
        self.__driver.execute_script(f"""
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
        sysstr = platform.system()
        windows = "windows"
        if (sysstr.lower() == windows):
            return True
        else:
            return False