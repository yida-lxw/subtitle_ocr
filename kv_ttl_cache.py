# -*- coding: utf-8 -*-
from cachetools import TLRUCache

from config.app_config import APPConfig
from utils.string_utils import StringUtils

project_basepath = StringUtils.get_project_basepath()
project_basepath = StringUtils.replaceBackSlash(project_basepath)
project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)


# 加载配置文件
app_config_path = "config/app.yml"
app_config_loaded = APPConfig.load_app_config(project_basepath, app_config_path)

def my_ttu(key, value, time, ttl=app_config_loaded.kv_cache_max_age):
    return time + ttl


class KVTTLCache:
    def __init__(self, kv_max_size: int = app_config_loaded.kv_cache_max_size, kv_max_age: int = app_config_loaded.kv_cache_max_age):
        self.kv_max_size = kv_max_size
        self.kv_max_age = kv_max_age
        self.kv_cache = TLRUCache(maxsize=self.kv_max_size, ttu=my_ttu)

    def get(self, key):
        return self.kv_cache.get(key)

    def set(self, key, value):
        self.kv_cache[key] = value

    def delete(self, key):
        value = self.kv_cache.pop(key)
        return value

    def contains(self, key):
        return key in self.kv_cache

    def clear(self):
        self.kv_cache.clear()
