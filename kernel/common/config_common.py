from kernel.base_class.base_class import *
import configparser
import os


class ConfigCommon(BaseClass):

    def __init__(self,args):
        pass

    def get_static(self,sub_dir):
        sub_dir = self.config_cfg("static",sub_dir)
        sub_dir = self.abs_dir__(sub_dir)
        return sub_dir

    def get_public(self,dir=None):
        sub_dir = self.config_cfg("static","public_dir")
        if dir != None:
            sub_dir = sub_dir + "/" + dir
        sub_dir = self.abs_dir__(sub_dir)
        return sub_dir

    def get_bin_dir(self,dir=None):
        sub_dir = self.config_cfg("static","bin_dir")
        if dir != None:
            sub_dir = sub_dir + "/" + dir
        sub_dir = self.abs_dir__(sub_dir)
        return sub_dir

    def get_template_dir(self,dir=None):
        sub_dir = self.config_cfg("static","template_dir")
        if dir != None:
            sub_dir = sub_dir + "/" + dir
        sub_dir = self.abs_dir__(sub_dir)
        return sub_dir

    def get_webdownload_dir(self):
        sub_dir = self.config_cfg("static","webdownload_dir")
        sub_dir = self.abs_dir__(sub_dir)
        return sub_dir

    def abs_dir__(self,dir):
        cwd = self.getcwd()
        dir = f"{ os.path.join(cwd,dir)}".replace('\\','/')
        if os.path.exists(dir) and os.path.isdir(dir):
            dir = dir+"/"
        return dir

    def config_cfg(self,section,key):
        cfg = self.config(type="cfg",section=section,key=key)
        return cfg

    def config_ini(self,section,key):
        cfg = self.config(type="ini",section=section,key=key)
        return cfg

    def getcwd(self):
        return os.path.abspath(__file__).split('kernel')[0]

    def config(self,type="cfg",section="",key=""):
        cwd = self.getcwd()
        cfg_path = os.path.join(cwd,"kernel/config.cfg")
        if type=="cfg":
            cfg_parser = configparser.RawConfigParser()
        if type=="ini":
            cfg_parser = configparser.ConfigParser()
        cfg_parser.read(cfg_path)
        cfg = cfg_parser[section][key]
        return cfg
