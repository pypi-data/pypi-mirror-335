# -*- coding: utf8 -*-

"hikepy全局配置类"

__author__ = "hnck2000@126.com"

import os
import time
from dataclasses import dataclass,field,asdict
import yaml
from .model import HkBaseData as baseData

@dataclass
class DBConfigData(baseData):
    """数据库配置类"""
    enable:bool=False
    url:str="mysql+aiomysql://user:password@localhost/dbname?charset=utf8mb4"
    pool_size:int=5
    max_overflow:int=10
    pool_timeout:int=30

@dataclass
class MogoConfigData(baseData):
    """MogoDB配置类"""
    enable:bool=False
    url:str="mongodb://admin:admin@127.0.0.1:27017"
    database:str="database"

@dataclass
class AppInfoData(baseData):
    """项目基本信息类"""
    title:str="hikepy生成项目"
    description:str="hikepy生成项目"
    summary:str="hikepy生成项目"
    version:str="0.0.1"
    contact:dict=field(default_factory=dict)

@dataclass
class RedisData(baseData):
    """缓存配置类"""
    enable:bool=False
    host:str="127.0.0.1"
    port:int=6379
    password:str=""
    db:int=0


@dataclass
class HkConfigData(baseData):
    """配置数据类"""
    env:str="dev"
    assets_path:str=field(default="",init=False)
    ip:str="0.0.0.0"
    port:int=8081
    appinfo:AppInfoData=field(default_factory=dict)
    cache:RedisData=field(default_factory=dict)
    database: DBConfigData=field(default_factory=dict)
    mogodb: MogoConfigData=field(default_factory=dict)
    custom:dict = field(default_factory=dict)

class HkConfig:
    """全局配置类"""
    SECRET_KEY:str = "3d78040d65bb4523da87bb71ba0728882a58e578fd88105a4a6d524e2735eeb6"
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS:str = 7

    def __init__(self):
        self.data:HkConfigData=HkConfigData()
        self.data.appinfo=AppInfoData(contact={
        "name": "wantao",
        "url": "https://github.com/",
        "email": "hnck2000@126.com",
    })
        self.data.cache=RedisData()
        self.data.database=DBConfigData()
        self.data.mogodb=MogoConfigData()
        self.json:dict=asdict(self.data)
        self.sid:str=str(int(time.time() * 1000))
        self.id_generator=self.id_generator_func()

    def load_config(self,assets_path:str,host:str,port:int,env:str="dev"):
        """加载配置文件"""
        self.data.env=env
        self.data.assets_path=assets_path
        #优先使用命令行参数
        if host:
            self.data.ip=host
        if port:
            self.data.port=port
        
        #判断是否存在配置文件，如果不存在生成一个
        config_file_path=os.path.join(assets_path,"etc","config-"+env+".yaml")
        if os.path.exists(config_file_path):
            with open(config_file_path, 'r',encoding="utf-8") as f:
                self.json=yaml.safe_load(f)
                self.data=self.data.copy(self.json)
                self.data.assets_path=assets_path
        else:
            with open(config_file_path, 'w+',encoding="utf-8") as f:
                self.json=asdict(self.data)
                del self.json["assets_path"]
                yaml.safe_dump(self.json, f)

    def id_generator_func(self):
        """主键生成器"""
        n = 0
        while(True):
            n += 1
            yield n    

    def id(self,prex:str="00",start:int=0,nlen:int=10):
        """主键生成，生成规则prex-sid-id"""
        nmlen=10 if nlen<10 else nlen
        nb=start+next(config.id_generator)
        prex_s="" if prex=="" else prex+"-"
        str_num = str(nb).zfill(nmlen)
        return f"{prex_s}{config.sid}-{str_num}"

config=HkConfig()
