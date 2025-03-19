# -*- coding: utf8 -*-

"hikepy日志记录类"

__author__ = "hnck2000@126.com"

import os
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler
from .config import config

class HkLogger:
    """日志记录类"""

    def __init__(self):
        self.loggers:dict[str,Logger]={}

    def get_logger(self,name:str)->Logger:
        """根据名称获取日志记录类"""
        if name in self.loggers:
            return self.loggers[name]
        else:
            new_logger = logging.getLogger(name)
            formatter = logging.Formatter("[%(asctime)s][%(levelname)s]: %(message)s")
            if config.data.env=="dev":
                new_logger.setLevel(logging.DEBUG)
            else:
                new_logger.setLevel(logging.INFO)

            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            # 创建文件处理器
            file_handler = RotatingFileHandler(os.path.join(config.data.assets_path,"logs", name+'.log'),maxBytes=5*1024*1024, backupCount=1)
            file_handler.setFormatter(formatter)

            # 将处理器添加到logger
            new_logger.addHandler(console_handler)
            new_logger.addHandler(file_handler)

            self.loggers[name]=new_logger
            return new_logger


    def set_env(self,level:int=logging.INFO,name:str="app"):
        """设置日志记录级别"""
        logger=self.get_logger(name)
        logger.setLevel(level)

    def debug(self,msg:str,name:str="app"):
        """debug"""
        logger=self.get_logger(name)
        logger.debug(msg)

    def info(self,msg:str,name:str="app"):
        """info"""
        logger=self.get_logger(name)
        logger.info(msg)

    def warning(self,msg:str,name:str="app"):
        """warning"""
        logger=self.get_logger(name)
        logger.warning(msg)

    def error(self,msg:str,name:str="app"):
        """error"""
        logger=self.get_logger(name)
        logger.error(msg)

    def critical(self,msg:str,name:str="app"):
        """critical"""
        logger=self.get_logger(name)
        logger.critical(msg)



hklog=HkLogger()
