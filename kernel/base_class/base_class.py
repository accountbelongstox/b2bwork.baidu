class BaseClass:
    def __setattr__(self, key, value):
        #print("__setattr__")
        self.__dict__[key] = value
    def __set__(self, instance, value):
        #print("__set__")
        self.__dict__[instance] = value

    def __get__(self, item):
        return self.__dict__.get(item)

    def __getattr__(self, item):
        return self.__dict__.get(item)

    def get_cwd(self):
        return __file__.split('kernel')[0]



