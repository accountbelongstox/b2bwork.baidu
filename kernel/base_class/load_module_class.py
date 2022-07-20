import importlib,importlib.util
import os

class LoadModuleClass:
    __kernel_name = "kernel"
    __commons_class = []
    __modes_class = []

    def add_module(self,control_module_name,module_name,argv):
        control = self.load_class(control_module_name,module_name,argv)
        self.load_kernel_class(module_type_name="common")
        self.load_kernel_class(module_type_name="mode")
        self.attach_module(self.__modes_class,"common")
        self.attach_module(self.__commons_class,"common")
        self.attach_module(control,"mode")
        self.attach_module(control,"common")
        return control

    def load_kernel_class(self,module_type_name="common"):
        module_path = self.get_module_dir(module_type_name)
        modules = os.listdir(module_path)
        modules = [m for m in modules if not m.startswith("__")]
        for m in modules:
            module_name = m.replace('.py', "")
            module = self.load_class(module_type_name,module_name)
            if module_type_name =="common":
                self.__commons_class.append(
                    (module_name , module)
                )
            elif module_type_name =="mode":
                self.__modes_class.append(
                    (module_name, module)
                )

    def get_module_dir(self,module):
        curdir = os.getcwd()
        module_dir = os.path.join(curdir, self.__kernel_name, module)
        return module_dir

    def get_kernel_module_name(self,module_type_name,module_name):
        module_name = f"{self.__kernel_name}.{module_type_name}.{module_name}"
        return module_name

    def attach_all_mode_to(self,control):
        self.attach_module(control,module_type_name="mode")


    def attach_module(self,module_or_modules,module_type_name="common"):
        if type(module_or_modules) != list:
            module_or_modules = [module_or_modules]
        index = 0
        for module_and_name_tuple in module_or_modules:
            if type(module_and_name_tuple) != tuple:
                module_or_modules[index] = (module_and_name_tuple.__class__.__name__,module_and_name_tuple)
                index+=1
        if module_type_name == "common":
            kernermodules = self.__commons_class
        elif module_type_name == "mode":
            kernermodules = self.__modes_class

        for module_and_name_tuple in module_or_modules:
            module = module_and_name_tuple[1]
            for kernremodule in kernermodules:
                simple_name = kernremodule[0]
                attach_module = kernremodule[1]
                module_name = attach_module.__class__.__name__
                is_module_attr = module.__getattr__(simple_name)
                if is_module_attr == None:
                    if module.__class__.__name__ != module_name:
                        module.__setattr__(simple_name,attach_module)

    def load_module_and_execute(self,control,module_type_name,module_name):
        # spec = self.load_module_fram_file(module_name, module_path)
        # module = importlib.util.module_from_spec(spec)
        # attach_module_name = f"{module_name}"
        # spec.loader.exec_module(module)
        #module = globals()[]
        pass


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