from kernel.base_class.base_class import *
import threading
import time


class ThreadCommon(BaseClass):  # 继承父类threading.Thread
    __threads = []

    def __init__(self):
        pass

    def create_thread(self, fn=None, args=(), thread_id=None, thread_name=None):
        thread = NewThread(fn, args, thread_id, thread_name)
        self.__threads.append(thread)
        return thread

    def get_thread(self, thread_name):
        is_id = True
        if type(thread_name) == str:
            is_id = False

        for thread in self.__threads:
            if is_id == True:
                thread_c = thread.get_name()
            else:
                thread_c = thread.get_id()
            if thread_c == thread_name:
                return thread
        return None

class NewThread(threading.Thread):  # 继承父类threading.Thread
    def __init__(self, fn, args, thread_id, thread_name):
        threading.Thread.__init__(self)
        self.fn = fn
        self.args = args
        self.thread_id = thread_id
        self.name = thread_name

    def run(self, ):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        if self.fn != None:
            self.fn(self.args)
        else:
            print("Not give Function")

    def get_id(self):
        return self.thread_id