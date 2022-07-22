import importlib,importlib.util
import os

class LoadModuleClass:
    __kernel_name = "kernel"
    __commons_class = {}
    __modes_class = {}

    def add_module(self,control_module_name,module_name=None,args=()):
        if type(control_module_name) == str:
            control = self.load_class(control_module_name,module_name,args)
        else:
            control = control_module_name
        self.load_kernel_class_init(args)
        self.attach_module(control,"mode",args)
        self.attach_module(control,"common",args)
        return control

    def load_kernel_class_init(self,args):
        self.load_kernel_class(module_type_name="common",args=args)
        self.load_kernel_class(module_type_name="mode",args=args)

    def load_kernel_class(self,module_type_name="common",args=()):
        if module_type_name == "common":
            module_init = len(self.__commons_class.keys()) == 0
            #模型模块已经提前载入，则要混淆
            that_modules = len(self.__modes_class.keys()) != 0
            #确认混淆
            before_load_that_modules = module_init and that_modules
        else:
            module_init = len(self.__modes_class.keys()) == 0
            #公用模块已经提前载入，则要混淆
            that_modules = len(self.__commons_class.keys()) != 0
            #确认混淆
            before_load_that_modules = module_init and that_modules

        if module_init:
            module_path = self.get_module_dir(module_type_name)
            modules = os.listdir(module_path)
            modules = [m for m in modules if not m.startswith("__")]
            for m in modules:
                module_name = m.replace('.py', "")
                module = self.load_class(module_type_name,module_name,args)
                if module_type_name =="common":
                    self.__commons_class[module_name] = module
                elif module_type_name =="mode":
                    self.__modes_class[module_name] = module
        # 确认混淆
        # 需要连续调用两次才能混淆
        if before_load_that_modules:
            self.attach_module(self.__modes_class, "common")
            self.attach_module(self.__commons_class, "common")
        if module_type_name == "common":
            return self.__commons_class
        else:
            return self.__modes_class

    def attach_module_from(self,module,attach_module_name):
        attach_module_name_parse = attach_module_name.split('_')
        attach_module_name_len = len(attach_module_name_parse)
        module_type = attach_module_name_parse[attach_module_name_len - 1]
        if module_type == "common":
            attach_module = self.__commons_class[attach_module_name]
        else:
            attach_module = self.__modes_class[attach_module_name]
        is_module_attr = module.__dict__.get(attach_module_name)
        if is_module_attr == None:
            module.__setattr__(attach_module_name, attach_module)

    def get_module_dir(self,module):
        curdir = os.getcwd()
        module_dir = os.path.join(curdir, self.__kernel_name, module)
        return module_dir

    def get_kernel_module_name(self,module_type_name,module_name):
        module_name = f"{self.__kernel_name}.{module_type_name}.{module_name}"
        return module_name

    def attach_all_mode_to(self,control):
        self.attach_module(control,module_type_name="mode")


    def attach_module(self,module_or_modules,module_type_name="common",args=()):
        if type(module_or_modules) != dict:
            module_or_modules = {
                module_or_modules.__class__.__name__: module_or_modules
            }
        if module_type_name == "common":
            kernermodules = self.__commons_class
        else:
            kernermodules = self.__modes_class

        for module_name,module in module_or_modules.items():
            for simple_name,attach_module in kernermodules.items():
                module_name = attach_module.__class__.__name__
                is_module_attr = module.__dict__.get(simple_name)
                if is_module_attr == None \
                        and \
                module.__class__.__name__ != module_name:
                    module.__setattr__(simple_name,attach_module)
                    try:
                        args = {
                            "args":args,
                            "module":module,
                        }
                        attach_module.main(args)
                    except:
                        continue

    def load_module_fram_file(self,module_name,module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        return spec

    def load_class(self,module_type_name,module_name, *args, **kwargs):
        module_load_name =  self.get_kernel_module_name( module_type_name, module_name)
        class_name = "".join([n.title() for n in module_name.split('_')])
        module_meta = __import__(module_load_name, globals(), locals(), [class_name])
        class_meta = getattr(module_meta, class_name)
        module = class_meta(*args, **kwargs)
        return module