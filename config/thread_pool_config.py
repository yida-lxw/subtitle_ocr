# -*- coding: utf-8 -*-
import multiprocessing
import os

import yaml
from yaml import YAMLError

from object_iterator import ObjectIterator, IteratorType
from utils.string_utils import StringUtils

# 获取CPU核数
cpu_core_size = multiprocessing.cpu_count()


class ThreadPoolConfigError(Exception):
    """自定义配置异常类"""
    pass


class ThreadPoolConfig:
    def __init__(self, concurrency_level: int = 5, max_pool_size: int = cpu_core_size * 2,
                 thread_name_prefix: str = "subtitle-extraction",
                 iteratorType: IteratorType = IteratorType.DICT):
        self.concurrency_level = concurrency_level
        self.max_pool_size = max_pool_size
        self.thread_name_prefix = thread_name_prefix
        self.iteratorType = iteratorType

    def getConcurrencyLevel(self) -> int:
        return self.concurrency_level

    def getMaxPoolSize(self) -> int:
        return self.max_pool_size

    def getThreadNamePrefix(self) -> str:
        return self.thread_name_prefix

    def setConcurrencyLevel(self, concurrency_level: int):
        self.concurrency_level = concurrency_level
        return self

    def setMaxPoolSize(self, max_pool_size: int):
        self.max_pool_size = max_pool_size
        return self

    def setThreadNamePrefix(self, thread_name_prefix: str):
        self.thread_name_prefix = thread_name_prefix
        return self

    @staticmethod
    def load_thread_pool_config(project_basepath=None, config_path="config/thread_pool.yml"):
        if StringUtils.is_empty(project_basepath):
            project_basepath = StringUtils.get_project_basepath()
        project_basepath = StringUtils.replaceBackSlash(project_basepath)
        project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)
        thread_pool_yml_file_path = os.path.join(project_basepath, config_path)
        return ThreadPoolConfig.load(file_path=thread_pool_yml_file_path)

    @classmethod
    def load(cls, file_path='config/thread_pool.yml'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        except FileNotFoundError:
            raise ThreadPoolConfigError(f"配置文件 {file_path} 未找到")
        except YAMLError as e:
            raise ThreadPoolConfigError(f"YAML解析错误: {e}")

        # 验证配置结构
        thread_config = config_data.get('thread')
        if not thread_config:
            raise ThreadPoolConfigError("配置文件中缺少 'thread'配置项")
        pool_config = thread_config.get('pool')
        if not pool_config:
            raise ThreadPoolConfigError("配置文件中缺少 'pool'配置项")

        # 验证必需字段
        required_fields = ['concurrency-level', 'max-pool-size']
        missing_fields = [field for field in required_fields if field not in pool_config]
        if missing_fields:
            raise ThreadPoolConfigError(f"缺少必需字段: {', '.join(missing_fields)}")

        if not isinstance(pool_config['concurrency-level'], int):
            raise ThreadPoolConfigError("concurrency-level必须为整型")

        if not isinstance(pool_config['max-pool-size'], int):
            raise ThreadPoolConfigError("max-pool-size必须为整型")

        if not isinstance(pool_config['thread-name-prefix'], str):
            raise ThreadPoolConfigError("thread-name-prefix必须为字符串类型")

        return cls(
            concurrency_level=pool_config['concurrency-level'],
            max_pool_size=pool_config['max-pool-size'],
            thread_name_prefix=pool_config['thread-name-prefix'],
        )

    def __iter__(self):
        # field_keys = list(self.__dict__.keys())
        field_dict = self.__dict__
        final_field_dict = {}
        final_field_keys = []
        for key, value in field_dict.items():
            if type(value) == IteratorType:
                continue
            final_field_keys.append(key)
            final_field_dict.update({key: value})
        return ObjectIterator(field_dict=final_field_dict, field_keys=final_field_keys, iteratorType=self.iteratorType)

    def __eq__(self, other):
        if isinstance(other, ThreadPoolConfig):
            return (self.concurrency_level == other.concurrency_level and self.max_pool_size == other.max_pool_size and
                    self.thread_name_prefix == other.thread_name_prefix)
        return False

    def __hash__(self):
        return hash(self)
