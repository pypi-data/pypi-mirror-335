# -*- coding: utf8 -*-

"hikepy启动类"

__author__ = "hnck2000@126.com"

import os
import inspect
import argparse
import pkgutil
import importlib
import json
import time
from typing import List, Annotated, Mapping, Any
import uvicorn
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import FastAPI, Request, status, APIRouter, HTTPException, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.background import BackgroundTask
from pydantic import ValidationError
from .hklogger import hklog
from .tools import hkcache, hk_db_manager, hk_mogo_manager
from .config import config
from .business import HkBusinessException
from .model import AuthInfo



# 定义一个异步函数的类型提示
class HkJSONResponse(Response):
    """自定义响应类"""

    media_type = "application/json"

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: Any) -> bytes:
        newcontent = {"code": self.status_code, "message": "", "data": content}
        result = json.dumps(
            newcontent,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")
        return result


class HkAuth:
    """jwt验证类"""

    def __init__(self, role: List[str] = None, act: List[str] = None):
        self.role = role
        self.act = act

    def __call__(
        self, token: Annotated[str | None, Header(description="auth token")] = None
    ) -> AuthInfo:
        credentials_exception=HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
            )

        if token is None:
            raise credentials_exception
        try:
            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            user_id: str = payload.get("user_id")
            user_roles: List[str]=payload.get("roles")
            user_acts: List[str]=payload.get("acts")
            data: dict = payload.get("data")
            if user_id is None:
                raise credentials_exception
            r_checked=False
            a_checked=False
            if self.role:
                if user_roles:
                    for r1 in self.role:
                        if r1 in user_roles:
                            r_checked=True
            else:
                r_checked=True

            if self.act:
                if user_acts:
                    for r1 in self.act:
                        if r1 in user_acts:
                            a_checked=True
            else:
                a_checked=True

            if not (r_checked and a_checked):
                raise credentials_exception
            return AuthInfo(user_id=user_id,data=data,roles=user_roles,acts=user_acts)
        except (InvalidTokenError, ValidationError) as exc:
            print(str(exc))
            raise credentials_exception from exc


class HkApp:
    """启动类"""

    def __init__(self):
        self.app: FastAPI = None
        self.prehook_caller = None
        self.routers: list[APIRouter] = []

    def init_assets(self, root_path: str):
        """初始化资源结构"""
        os.makedirs(os.path.join(root_path, "assets"), exist_ok=True)
        os.makedirs(os.path.join(root_path, "assets", "etc"), exist_ok=True)
        os.makedirs(os.path.join(root_path, "assets", "logs"), exist_ok=True)

    def prehook(self, func):
        """初始化钩子装饰器"""

        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        self.prehook_caller = wrapper
        return wrapper

    def get_fastapi_logconfig(self) -> dict:
        """设置fastapi日志格式及路径"""
        log_path = os.path.join(config.data.assets_path, "logs", "access.log")
        server_log_path = os.path.join(config.data.assets_path, "logs", "server.log")
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "[%(asctime)s][%(levelname)s]: %(message)s",
                    "use_colors": None,
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": '[%(asctime)s][%(levelname)s]: %(client_addr)s - "%(request_line)s" %(status_code)s',
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "default_file": {
                    "formatter": "default",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": server_log_path,
                },
                "access_file": {
                    "formatter": "access",
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "filename": log_path,
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default", "default_file"], "level": "INFO"},
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {
                    "handlers": ["access_file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }

    def scan_routers(self, router_root: str, pkg_path: str):
        """扫描指定包下的路由文件"""
        for module in pkgutil.walk_packages([router_root], pkg_path + "."):
            if module.ispkg:
                self.scan_routers(os.path.join(router_root, module.name), module.name)
            else:
                if module.name.split(".")[-1] == "routers":
                    router = importlib.import_module(module.name)
                    for name, value in router.__dict__.items():
                        if name == "router" and isinstance(value, APIRouter):
                            self.routers.append(value)

    def scan_service(self, service_root: str, pkg_path: str):
        """扫描指定包下的路由文件"""
        for module in pkgutil.walk_packages([service_root], pkg_path + "."):
            if module.ispkg:
                self.scan_service(os.path.join(service_root, module.name), module.name)
            else:
                if module.name.split(".")[-1] == "service":
                    importlib.import_module(module.name)

    def get_startup(self, root_path: str, router_root: str):
        """定义fastapi初始化事件"""
        self.scan_service(
            os.path.join(root_path, router_root.replace(".", os.sep)), router_root
        )

        async def start_app():
            # 创建数据库
            await hk_db_manager.register_database(
                os.path.join(root_path, router_root.replace(".", os.sep)), router_root
            )
            # 留给研发进行扩展启动方法
            if self.prehook_caller:
                await self.prehook_caller()
                hklog.info("prehook exec completed")
            else:
                hklog.info("prehook not set")

        return start_app

    def start(self, autostar: bool = True, router_root: str = "app.modules"):
        """开启服务"""
        print("server init....")
        caller_file = inspect.getfile(inspect.currentframe().f_back)
        root_path = os.path.dirname(caller_file)
        # 判断当前环境
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "arg1", help="应用当前环境", type=str, nargs="?", default="dev"
        )
        parser.add_argument("--host", help="IP地址", type=str, required=False)
        parser.add_argument("--port", help="监听端口", type=int, required=False)

        args = parser.parse_args()
        # 初始化资源目录
        print("server assets init......")
        self.init_assets(root_path)
        print("server config init......")
        # 初始化全局配置
        config.load_config(
            os.path.join(root_path, "assets"), args.host, args.port, args.arg1
        )
        hklog.info("env check completed,current env is " + args.arg1)
        hklog.info("assets check completed")
        hklog.info("config load completed")
        hklog.debug(config.data.__dict__)

        # 业务工具初始化
        if "cache" in config.json and config.json["cache"]["enable"]:
            hkcache.init(
                host=config.json["cache"]["host"],
                port=config.json["cache"]["port"],
                password=config.json["cache"]["password"],
                decode_responses=True,
                db=config.json["cache"]["db"]
            )
        if "database" in config.json and config.json["database"]["enable"]:
            hk_db_manager.init(
                url=config.json["database"]["url"],
                pool_size=config.json["database"]["pool_size"],
                max_overflow=config.json["database"]["max_overflow"],
                pool_timeout=config.json["database"]["pool_timeout"],
            )

        if "mogodb" in config.json and config.json["mogodb"]["enable"]:
            hk_mogo_manager.init(
                config.json["mogodb"]["url"], config.json["mogodb"]["database"]
            )

        self.app = FastAPI(
            default_response_class=HkJSONResponse,
            title=config.json["appinfo"]["title"],
            description=config.json["appinfo"]["description"],
            summary=config.json["appinfo"]["summary"],
            version=config.json["appinfo"]["version"],
            contact=config.json["appinfo"]["contact"],
            Response="",
            openapi_url=None,
            docs_url=None,
            redoc_url=None
        )

        # 自定义异常处理
        @self.app.exception_handler(HkBusinessException)
        async def business_exception_handler(
            request: Request, exc: HkBusinessException
        ):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"code": exc.code, "message": exc.message},
            )

        @self.app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"code": exc.status_code, "message": str(exc.detail)},
            )

        @self.app.exception_handler(HTTPException)
        async def http_exception_fastapi_handler(request: Request, exc: HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"code": exc.status_code, "message": str(exc.detail)},
            )

        @self.app.exception_handler(ValidationError)
        async def pydict_validation_exception_handler(
            request: Request, exc: ValidationError
        ):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "错误的请求参数",
                },
            )

        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(
            request: Request, exc: RequestValidationError
        ):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": str(exc),
                    "body": exc.body,
                },
            )

        # 跨域中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 自定义中间件
        @self.app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.perf_counter()
            response = await call_next(request)
            process_time = round(time.perf_counter() - start_time, 4)
            response.headers["X-Process-Time"] = str(process_time)
            hklog.info("URL:" + request.url.path + " time:" + str(process_time))
            return response

        # 自定义全局注入

        # 添加自定义事件
        self.app.add_event_handler("startup", self.get_startup(root_path, router_root))

        # 扫描路径自动加载路由
        self.scan_routers(
            os.path.join(root_path, router_root.replace(".", os.sep)), router_root
        )
        for router in self.routers:
            self.app.include_router(router)

        # 开启fastapi服务
        hklog.info("server started")
        if autostar:
            log_config = self.get_fastapi_logconfig()
            uvicorn.run(
                self.app,
                host=config.data.ip,
                port=config.data.port,
                log_config=log_config,
            )


hkapp = HkApp()
