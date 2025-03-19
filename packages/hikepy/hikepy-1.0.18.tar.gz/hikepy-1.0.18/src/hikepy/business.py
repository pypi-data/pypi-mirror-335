# -*- coding: utf8 -*-

"hikepy业务核心类"

__author__ = "hnck2000@126.com"

import time
import inspect
import httpx
from redis import Redis

# from typing import Annotated,get_args
from .hklogger import hklog
from .tools import hkcache, Sql, hk_db_manager,hk_mogo_manager,Mogo,Rest


class HkBusinessException(Exception):
    """自定义业务异常"""

    def __init__(self, code: int = 0, message: str = ""):
        """构造函数"""
        self.code = code
        self.message = message

def service(func):
    """业务方法装饰器"""

    async def wrapper(*args, **kwargs):
        # annotations = func.__annotations__
        func_sig = inspect.signature(func)
        start_time = time.perf_counter()
        func_file = inspect.getfile(func)
        sql_session = None
        cache_inst = None
        rest_client = None
        in_transcation=False
        hklog.info("enter service:" + func.__name__ + " file:" + func_file)
        try:
            for _, param in func_sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    arg_class = None
                    # arg_meta=None
                    # anno_meta=get_args(param.annotation)
                    # if len(anno_meta)>0:
                    #    arg_class=anno_meta[0]
                    #    arg_meta=anno_meta[1]
                    # else:
                    #    arg_class=param.annotation
                    arg_class = param.annotation
                    if issubclass(arg_class, Sql):
                        # 数据库工具装入
                        # if anno_meta:
                        #    sql_inst=arg_class(**arg_meta.__dict__)
                        # else:
                        #    sql_inst=arg_class()
                        if kwargs.get(param.name):
                            sql_session=kwargs[param.name]
                            in_transcation=True
                        
                        if sql_session is None:
                            sql_session = hk_db_manager.create_session()
                            await sql_session.begin()
                            kwargs[param.name] = Sql(sql_session)
                    elif issubclass(arg_class, Redis):
                        # Cache工具装入
                        cache_inst = hkcache.client()
                        kwargs[param.name] = cache_inst
                    elif issubclass(arg_class, Mogo):
                        # mogo工具装入
                        kwargs[param.name] = hk_mogo_manager.db
                    elif issubclass(arg_class, Rest):
                        # rest工具装入
                        rest_client = httpx.AsyncClient()
                        kwargs[param.name] = Rest(rest_client)   

            result = await func(*args, **kwargs)
            if sql_session and in_transcation is False:
                await sql_session.commit()
        except HkBusinessException as e:
            hklog.error(f"raise business code:{e.code} message:{e.message}")
            if sql_session and in_transcation is False:
                await sql_session.rollback()
            raise
        except Exception as ext:
            hklog.error(f"service:{func.__name__} file:{func_file} error:{str(ext)}")
            if sql_session and in_transcation is False:
                await sql_session.rollback()
            raise HkBusinessException(400, "当前服务发异常") from ext
        finally:
            if sql_session and in_transcation is False:
                await sql_session.close()
            if cache_inst:
                cache_inst.close()
            if rest_client:
                await rest_client.aclose()    

            sql_session = None
            cache_inst = None
            sql_session = None
            rest_client = None
            in_transcation=False
            process_time = round(time.perf_counter() - start_time, 4)
            hklog.info(
                "leave service:"
                + func.__name__
                + " file:"
                + func_file
                + " time:"
                + str(process_time)
            )
        return result
    return wrapper
