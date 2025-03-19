# -*- coding: utf8 -*-

"hikepy基础数据类"

__author__ = "hnck2000@126.com"
from typing import TypeVar,List,Any,Optional
from datetime import datetime
from dataclasses import dataclass,replace,asdict
from pydantic import BaseModel,Field
from sqlalchemy import DATETIME,String,CHAR,Column
from sqlalchemy.orm import DeclarativeBase

class HkBaseModel(BaseModel):
    """pydantic基础类"""

class Base(DeclarativeBase):
    """数据库模型基础类"""
    def model_dump(self):
        """将 SQLAlchemy 模型实例转换为字典"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class MogoModel(BaseModel):
    """mogo基础类"""
    id:str=Field(min_length=1,max_length=64,alias="_id")
    create_user:Optional[str]=Field(default=None,min_length=1,max_length=50)
    update_user:Optional[str]=Field(default=None,min_length=1,max_length=50)
    is_delete:str=Field(default="N", min_length=1,max_length=100)
    create_time:datetime=Field(default_factory=datetime.now)
    update_time:datetime=Field(default_factory=datetime.now)

    def model_dump(self):
        """重写model_dump方法，默认使用别名"""
        return super().model_dump(by_alias=True)

class SqlModel(Base):
    """所有数据库模型都需要集成此类"""
    # 定义为抽象类
    __abstract__ = True
    # 默认字段
    id = Column(String(50),primary_key=True,comment="主键")
    create_user = Column(String(50),nullable=True,comment="创建人")
    create_time = Column(DATETIME,default=datetime.now, comment="创建时间")
    update_user = Column(String(50),nullable=True, comment="更新人")
    update_time = Column(DATETIME,default=datetime.now, comment="更新时间")
    is_delete = Column(CHAR(1), default="N", comment="删除标识：N-正常 Y-已删除")

class PageList(HkBaseModel):
    """分页查询返回结果封装类"""
    page_size:int=1
    current_page:int=1
    total_size:int=0
    total_page:int=0
    datas:List[Any]=[]

    @classmethod
    def create(cls,datas:List[Any],current_page:int=1,total_size:int=0,page_size:int=1):
        """创建分页对象"""
        total_size = 0 if total_size<=0 else total_size
        page_size = 1 if page_size<=0 else page_size
        total_page=total_size//page_size if total_size % page_size == 0 else total_size//page_size+1
        return cls(datas=datas,current_page=current_page,total_size=total_size,page_size=page_size,total_page=total_page)


Self = TypeVar('Self',bound='HkBaseData')
@dataclass
class HkBaseData:
    """基础数据类"""

    def copy(self,data:Self)->Self:
        """替换数据属性返回新的实例，如果源数据没有对于属性则忽略"""
        if data:
            if isinstance(data, HkBaseData):
                return replace(self, **data.__dict__)
            else:
                return replace(self, **data)
        return self

    def merge(self,data:Self)->Self:
        """合并两个对象"""
        if data:
            data_org=asdict(self)
            data_dest=asdict(data) if isinstance(data, HkBaseData) else data
            new_data={**data_org, **data_dest}
            return HkBaseData(**new_data)
        return self

class AuthInfo(HkBaseModel):
    """jwt用户信息"""
    user_id:str
    roles:List[str]=[]
    acts:List[str]=[]
    data:dict={}

class CommonModel(HkBaseModel):
    """通用参数类"""
    keyword:str=Field(default="",description="关键字")
    page_size:int=Field(default=20,description="每页数量")
    current_page:int=Field(default=1,description="当前页码")
    order_by:str=Field(default="",description="排序字段")
    
