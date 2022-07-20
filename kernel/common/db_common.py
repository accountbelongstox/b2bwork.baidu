from kernel.base_class.base_class import *
from pymongo import MongoClient
import redis
import json
import os
import pickle

class DbCommon(BaseClass):
    __mongodb = None
    __redis = None
    __db_list = []
    __db_name = "base_py_mongodb"
    __db = None
    __db_prefix = "pr_"

    def __init__(self):
        pass

    def connect(self):
        if self.__db != None:
            return self.__db
        if self.__mongodb == None:
            self.__mongodb = MongoClient('mongodb://localhost:27017/')
        self.__db = self.__mongodb[self.__db_name]
        return self.__db

    def connect_redis(self):
        if self.__redis == None:
            #self.__redis = redis.StrictRedis(host='localhost', port=6379, db=0)
            pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
            self.__redis = redis.Redis(connection_pool=pool)
        return self.__redis

    def get_serialization_default_dir(self,file_path=None):
        if file_path == None:
            file_path = "public_data_serialization.list"
        core_data_dir = self.config_common.get_public(f"/core_data/{file_path}")
        return core_data_dir

    def serialization(self,obj,file_path=None):
        file_path = self.get_serialization_default_dir(file_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            old_obj = self.unserialization(file_path)
            if type(old_obj) == dict and type(obj) == dict:
                for k,v in obj.items():
                    old_obj[k] = v
            if type(old_obj) == list and type(obj) == list:
                for data in obj:
                    if data not in old_obj:
                        old_obj.append(data)
            obj = old_obj
        print(f"serialization data to {file_path}")
        file = open(file_path,'wb+')
        pickle.dump(obj,file,pickle.HIGHEST_PROTOCOL)

    def unserialization(self,file_path=None):
        file_path = self.get_serialization_default_dir(file_path)
        print(f"unserialization data from {file_path}")
        if os.path.exists(file_path) and os.path.isfile(file_path):
            file = open(file_path,'rb')
            try:
                obj = pickle.load(file)
                return obj
            except:
                return None
        else:
            return None


    def set_redis(self,dicts):
        redisdb = self.connect_redis()
        if type(dicts) != list:
            dicts = [dicts]
        for dic_itme in dicts:
            for k,v in dic_itme.items():

                if type(v) == list:
                    if len(v) > 0 : redisdb.lpush(k, *v)
                elif type(v) == set:
                    if len(v) > 0 :redisdb.sadd(k, *v)
                else:
                    if k.startswith('list'):
                        if len(v) > 0 :redisdb.lpush(k, v)
                    elif k.startswith('set'):
                        if len(v) > 0 :redisdb.sadd(k, v)
                    else:
                        redisdb.set(k,v)

    def remove_redis(self,key):
        redisdb = self.connect_redis()
        redisdb.delete(key)

    def get_redis_list(self,key,condition=[0,-1]):
        redisdb = self.connect_redis()
        datas = redisdb.lrange(key,*condition)
        if datas != None:
            datas = [t.decode("utf-8") for t in datas]
        return datas

    def get_redis_set(self,key):
        redisdb = self.connect_redis()
        datas = redisdb.smembers(key)
        return datas


    def get_redis(self,key,condition=[0,-1]):
        if key.startswith('list'):
            datas = self.get_redis_list(key,condition)
        elif key.startswith('set'):
            datas = self.get_redis_set(key)
        else:
            redisdb = self.connect_redis()
            datas = redisdb.get(key)
            if datas !=None:
                datas = json.loads(datas)
        return datas

    def save_data_to(self,collection_name,data):
        print("save_data_to",type(data))
        collection = self.create_collection(collection_name)
        if type(data) == dict:
            x = collection.insert_one(data)
            print(f" save_data_toinsert {len(x.inserted_id)} item")
        elif type(data) == list and len(list) > 0:
            x = collection.insert_many(data)
            print(f" save_data_toinsert {len(x.inserted_ids)} item")
        else:
            print("save_data_to => not support format")

    def read_data_to(self,collection_name,condition):

        collection = self.create_collection(collection_name)

        if "limit" in condition:
            new_con = {}
            for k,v in condition.items():
                if k != "limit":
                    new_con[k] = v
            result = collection.find(new_con).limit(condition["limit"])
        else:
            result = collection.find(condition)
        datas = []
        for data in result:
            datas.append(data)
        return datas

    def get_prefix_dbname(self,dbname):
        return f"{self.__db_prefix}{dbname}"

    def create_collection(self,dbname):
        self.connect()
        dbname = self.get_prefix_dbname(dbname)
        return self.__db[dbname]



