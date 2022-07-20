import os
import re
import sys

import scrapy
class OkxSpider(scrapy.Spider):
    name = 'okx'
    allowed_domains = ['www.okx.com']
    start_urls = ['http://www.okx.com/']

    def parse(self, response):
        body = response.body.decode('utf-8','strict')
        f = open('test.html','w',encoding="utf-8")
        f.write(body)
        pass
