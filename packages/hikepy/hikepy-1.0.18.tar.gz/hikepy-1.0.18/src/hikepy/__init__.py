"""
hikepy framework
"""

from .app import hkapp,HkAuth
from .hklogger import hklog
from .tools import hkcache
from .tools import hk_db_manager,hk_mogo_manager,create_token
from .config import config
from .model import HkBaseData as baseData,HkBaseModel as baseModel,SqlModel,PageList,AuthInfo,CommonModel,MogoModel
from .business import HkBusinessException,service

__version__ = '1.0.0'

__all__ = [
    '__version__',
    'hkapp',
    'hklog',
    'config',
    'baseData',
    'baseModel',
    'HkBusinessException',
    'service',
    'hkcache',
    'hk_db_manager',
    'SqlModel',
    'MogoModel',
    'PageList',
    'hk_mogo_manager',
    'AuthInfo',
    'HkAuth',
    'create_token',
    'CommonModel'
]

def __dir__() -> list[str]:
    return __all__
