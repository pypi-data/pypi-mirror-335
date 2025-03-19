# FastApi快速开发框架

本项目是基于fastapi为基础实现的开发框架。主要特点是简化代码量，内置ORM、Mongo、Cache等多种常见开发工具。结构简洁开包即用，框架自动扫描引入业务代码。

----

## 框架结构

```python
app--------------------------------应用包
    modules------------------------业务模块
        base-----------------------业务聚合1
            models.py--------------业务数据模型
            routers.py-------------Rest api接口
            service.py-------------业务逻辑
        foo------------------------业务聚合2
        foo2-----------------------业务聚合3
        foo3-----------------------业务聚合4
assets-----------------------------应用资源
    etc----------------------------应用配置
    logs---------------------------应用日志
app.py-----------------------------启动程序            
```

## 配置文件

配置环境区分
```python
python app.py 环境(dev prod 其他环境)
```
每个环境会生成对应的配置文件

```python
appinfo:
  contact:
    email: hnck2000@126.com
    name: wantao
    url: https://github.com/
  description: "应用介绍"
  summary: "应用简介"
  title: "应用名称"
  version: 0.0.1
cache:
  enable: false
  host: 127.0.0.1
  password: ''
  port: 6379
custom: {}#自定义配置
database:
  enable: true
  max_overflow: 10
  pool_size: 5
  pool_timeout: 30
  url: mysql+aiomysql://root:root@127.0.0.1/test?charset=utf8mb4
mogodb:
  enable: true
  url: mongodb://admin:admin@127.0.0.1:27017
  database: test   
env: dev
ip: 127.0.0.1
port: 8081

```
通过引入config使用全局配置数据
```python
from hikepy import config
```

## Routers

Routers文件是当前业务集合的所有接口程序部分，接口定义完全使用fastapi规范和语法

### 接口启用权限验证

```python
from hikepy import AuthInfo,HkAuth

async def read_users(authInfo:AuthInfo=Depends(HkAuth())):
```
通过引入HkAuth()依赖对该接口实现安全验证,请求此接口必须在Header中带有ticket=Token

### 生成token
```python
from hikepy import AuthInfo,HkAuth,create_token

return create_token(AuthInfo(user_id="test"))
```
通过create_token创建AuthInfo对象创建token

## Service

service.py是业务集合中所有的核心业务代码。

### 定义业务方法
```python
from hikepy import service

@service
async def foo():
```
通过@service装饰器定义业务方法，框架会自动扫描带有@service的方法

### 使用SQL
```python
from hikepy import service
from hikepy.tools import Sql

@service
async def foo(db:Sql=None):
```
通过在业务类方法上定义Sql类型提示来使用sql功能，框架会自动创建封装sql工具类，直接使用即可，例如：db.execute()

Sql工具类基于sqlalchemy封装，支持所有的sqlalchemy方法，封装了例如分页查询等方法db.page(select(TestModel))

关于事物嵌套，主方法调用子方法默认不开启事物嵌套，子方法会使用独立事物，如果要开启，在主方法调用子方法是需要给子方法传递db：Sql参数

### 使用Cache
```python
from hikepy import service
from redis import Redis

@service
async def foo(cache:Redis=None):
```
通过在业务类方法上定义Redis类型提示来使用cache功能， Redis未做封装直接使用python的Redis客户端

### 使用MogoDB
```python
from hikepy import service
from hikepy.tools import Mogo
@service
async def foo(mogo:Mogo=None):
```
通过在业务类方法上定义Mogo类型提示来使用mogo功能， mogo:Mogo是基于motor封装的mogo工具类，使用过程中采用异步模式

## Models

models.py是业务集合中所有用到的数据模型对象,数据模型以pydantic为基础进行封装。

```python
class HkBaseModel(BaseModel):
    """pydantic基础类"""
```
HkBaseModel是所有数据模型的基类，所有自定义模型应继承

```python
class SqlModel(Base):
    """所有数据库模型都需要集成此类"""
    # 定义为抽象类
    __abstract__ = True
    # 默认字段
    id = Column(String(50),primary_key=True,comment="主角")
    create_user = Column(String(50),nullable=True,comment="创建人")
    create_time = Column(DATETIME,default=datetime.now, comment="创建时间")
    update_user = Column(String(50),nullable=True, comment="更新人")
    update_time = Column(DATETIME,default=datetime.now, comment="更新时间")
    is_delete = Column(CHAR(1), default="N", comment="删除标识：0-正常 1-已删除")
```
SqlModel是所有ORM数据模型的基类，所有自定义模型应继承，定为数据表ORM模型时继承，已经内置了ID等属性，所有自定义类不在设置主键字段

```python
class PageList(Generic[T],HkBaseModel):
    """分页查询返回结果封装类"""
```
分页查询对象封装类型,分页查询会返回此类型

```python
class AuthInfo(HkBaseModel):
    """jwt用户信息"""
```
JWT的playload装载内容对象

```python
class CommonModel(HkBaseModel):
    """通用参数类"""
    keyword:str=Field(default="",description="关键字")
    page_size:int=Field(default=20,description="每页数量")
    current_page:int=Field(default=1,description="当前页码")
    order_by:str=Field(default="",description="排序字段")
```
通用查询参数封装类，用于从前端接收get/post传参，内置了一些常用的参数，使用时可以继承此类

## 常用工具

本项目是基于fastapi为基础实现的开发框架。主要特点是简化代码量，内置ORM、Mongo、Cache等多种常见开发工具。结构简洁开包即用，框架自动扫描引入业务代码。

### 全局主键生成器

```python
from hikepy import config

id=config.id()
```

通过config.id()方法生成全局唯一主键
