# -*- coding: utf-8 -*-
import os

import yaml
from yaml import YAMLError

from object_iterator import ObjectIterator, IteratorType
from utils.string_utils import StringUtils


class DBConfigError(Exception):
    pass


class DBConfig:
    def __init__(self, host: str, port: int, username: str, password: str, db_name: str, db_dir: str,
                 maxConnectionSize: int, initConnectionSize: int, maxIdleSize: int, charset: str = "utf8",
                 blockingIfNoConnection: bool = True, iteratorType: IteratorType = IteratorType.DICT):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db_name = db_name
        self.db_dir = db_dir
        self.charset = charset
        self.maxConnectionSize = maxConnectionSize
        self.initConnectionSize = initConnectionSize
        self.maxIdleSize = maxIdleSize
        self.blockingIfNoConnection = blockingIfNoConnection
        self.iteratorType = iteratorType

    @staticmethod
    def load_db_config(project_basepath=None, config_path="config/db.yml"):
        if StringUtils.is_empty(project_basepath):
            project_basepath = StringUtils.get_project_basepath()
        project_basepath = StringUtils.replaceBackSlash(project_basepath)
        project_basepath = StringUtils.to_ends_with_back_slash(project_basepath)
        db_yml_file_path = os.path.join(project_basepath, config_path)
        return DBConfig.load(file_path=db_yml_file_path)

    @classmethod
    def load(cls, file_path='config/db.yml'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        except FileNotFoundError:
            raise DBConfigError(f"配置文件 {file_path} 未找到")
        except YAMLError as e:
            raise DBConfigError(f"YAML解析错误: {e}")

        # 验证配置结构
        db_config = config_data.get('database')
        if not db_config:
            raise DBConfigError("配置文件中缺少 'database'配置项")

        # 验证必需字段
        required_fields = ['db-dir', 'db-name']
        missing_fields = [field for field in required_fields if field not in db_config]
        if missing_fields:
            raise DBConfigError(f"缺少必需字段: {', '.join(missing_fields)}")

        if not isinstance(db_config['db-dir'], str):
            raise DBConfigError("db-dir必须为str类型")

        if not isinstance(db_config['db-name'], str):
            raise DBConfigError("db-name必须为字符串类型")

        return cls(
            host=db_config['host'],
            port=db_config['port'],
            username=db_config['username'],
            password=db_config['password'],
            db_dir=db_config['db-dir'],
            db_name=db_config['db-name'],
            charset=db_config['charset'],
            maxConnectionSize=db_config['max-connection-size'],
            initConnectionSize=db_config['init-connection-size'],
            maxIdleSize=db_config['max-idle-size'],
            blockingIfNoConnection=db_config['blocking-if-no-connection']
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

    # getter
    def getHost(self):
        return self.host

    def getPort(self):
        return self.port

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def getDbName(self):
        return self.db_name

    def getDbDir(self):
        return self.db_dir

    def getCharset(self):
        return self.charset

    def getBlockingIfNoConnection(self):
        return self.blockingIfNoConnection

    def getMaxConnectionSize(self):
        return self.maxConnectionSize

    def getInitConnectionSize(self):
        return self.initConnectionSize

    def getMaxIdleSize(self):
        return self.maxIdleSize

    # setter
    def setHost(self, host: str):
        self.host = host
        return self

    def setPort(self, port: int):
        self.port = port
        return self

    def setUsername(self, username: str):
        self.username = username
        return self

    def setPassword(self, password: str):
        self.password = password
        return self

    def setDbName(self, db_name: str):
        self.db_name = db_name
        return self

    def setDbDir(self, db_dir: str):
        self.db_dir = db_dir
        return self

    def setCharset(self, charset: str):
        self.charset = charset
        return self

    def setBlockingIfNoConnection(self, blockingIfNoConnection: bool):
        self.blockingIfNoConnection = blockingIfNoConnection
        return self

    def setMaxConnectionSize(self, maxConnectionSize: int):
        self.maxConnectionSize = maxConnectionSize
        return self

    def setInitConnectionSize(self, initConnectionSize: int):
        self.initConnectionSize = initConnectionSize
        return self

    def setMaxIdleSize(self, maxIdleSize: int):
        self.maxIdleSize = maxIdleSize
        return self

    def __eq__(self, other):
        if isinstance(other, DBConfig):
            return (self.host == other.host and self.port == other.port and
                    self.db_name == other.db_name and self.db_dir == other.db_dir and
                    self.username == other.username and self.password == other.password and
                    self.charset == other.charset and self.blockingIfNoConnection == other.blockingIfNoConnection and
                    self.maxConnectionSize == other.maxConnectionSize and
                    self.initConnectionSize == other.initConnectionSize and self.maxIdleSize == other.maxIdleSize)
        return False

    def __hash__(self):
        return hash(self)
