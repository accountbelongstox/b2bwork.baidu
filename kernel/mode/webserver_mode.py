from kernel.base_class.base_class import *
import os
import re
import time
import socket
from urllib.parse import urlparse
# from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import threading
import sched
# from flask import Flask
# import json
# import mimerender
#
# app = Flask(__name__)

class WebserverMode(BaseClass):
    def __init__(self):
        pass

    def create_server(self,target="",port=18080):
        # app.run(port=port)
        pass
