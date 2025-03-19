import os
import json
from typing import Any, Dict


class SysConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SysConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # 确保 __init__ 只执行一次
            # 获取工程的根目录
            self.root_dir = os.path.abspath(os.path.dirname(__file__))

            # 获取资源目录
            self.resource_dir = os.path.join(self.root_dir, 'resources')

            # 获取配置文件路径
            self.config_file = os.path.join(self.resource_dir, 'sys_config.json')

            # 读取配置文件
            self.config = self.__load_config()

            self.initialized = True

    @classmethod
    def root_dir(cls):
        return cls._instance.root_dir

    @classmethod
    def resource_dir(cls):
        return cls._instance.resource_dir

    @classmethod
    def get(cls, key: str, default=None):
        return cls._instance.config.get(key, default)

    @classmethod
    def get_datasource_info(cls)->Dict[str, Any]:
        return cls._instance.config.get("datasource")

    def __load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件 {self.config_file} 不存在")

        with open(self.config_file, 'r', encoding='utf-8') as file:
            config = json.load(file)
        return config
