from kernel.base_class.base_class import *
import os
import zipfile
import shutil
import pickle

class FileCommon(BaseClass):

    def __init__(self,args):
        pass

    def load_file(self,file_name,encoding="utf-8"):
        if encoding == "binary":
            f = open(file_name, f"rb+")
        else:
            f = open(file_name, f"r+",encoding=encoding)
        content = f.read()
        f.close()
        return content

    def load_js(self,file_name,encoding="utf-8"):
        template_dir = self.config_common.get_js_dir()
        file_path = os.path.join(template_dir,file_name)
        content = self.load_file(file_path,encoding)
        return content

    def load_html(self,file_name,encoding="utf-8"):
        template_dir = self.config_common.get_template_dir()
        file_path = os.path.join(template_dir,file_name)
        content = self.load_file(file_path,encoding)
        return content

    def save_file(self,file_name,content,encoding=None,override=False):
        basename = os.path.dirname(file_name)
        # print(f"save-file ：{file_name}．")
        if os.path.exists(basename) is not True and os.path.isdir(basename) is not True:
            self.mkdir(basename)
        if override ==True:
            m = "w"
        else:
            m = "r"
        if encoding == None:
            f = open(file_name, f"{m}b+")
        else:
            f = open(file_name, f"{m}+",encoding=encoding)
        f.write(content)
        f.close()
        return True

    def zip_extract(self,file,member,o=None):
        if o == None:
            o = os.path.dirname(file)
        with zipfile(file) as f:
            f.extract(member,o)

    def zip_extractall(self,file,odir=None,member=None):
        if odir == None:
            odir = os.path.dirname(file)
        with zipfile.ZipFile(file) as f:
            f.extractall(odir,member)
        return odir

    def remove(self,top_path):
        print("delete : " ,top_path)
        for root, dirs, files in os.walk(top_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        if os.path.isdir(top_path):
            os.rmdir(top_path)
        elif os.path.isfile(top_path):
            os.remove(top_path)

    def mkdir(self, dir):
        if os.path.exists(dir) and os.path.isdir(dir):
            return False
        else:
            os.makedirs(dir,exist_ok=True)
            return True

        #shutil.rmtree(top_path)
