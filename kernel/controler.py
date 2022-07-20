from kernel.base_class.load_module_class import *

class Controler:

    def __init__(self, argv,):
        try:
            module_name = argv[1]
        except KeyError:
            print(KeyError,f" need parameter;")
            return
        LoadModule_Class = LoadModuleClass()
        control_module_name = "control"
        control = LoadModule_Class.add_module(control_module_name,module_name,argv)
        control.main(argv)
