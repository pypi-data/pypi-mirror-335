import logging
import os
import copy
from typing import Union, Dict, Optional
from configparser import ConfigParser

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
    get_redoc_html,
)

logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

FASTAPI_SETTINGS_MODULE = "FASTAPI_SETTINGS_MODULE"


def set_settings_module(module: str = "settings.ini"):
    os.environ.setdefault(FASTAPI_SETTINGS_MODULE, module)


def setup_routes(
    app: FastAPI,
    docs_url: str = "/docs",
    redoc_url: str = "/redoc",
):
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get(docs_url, include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get(redoc_url, include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
        )


def builder_fastapi(deploy: Union[Dict, FastAPI, None] = None, fastapi_settings: Optional[Dict] = None) -> FastAPI:
    if isinstance(deploy, FastAPI):
        return deploy
    config = copy.deepcopy(deploy or fastapi_settings or {})

    docs_url = config.pop("docs_url", "/docs")
    redoc_url = config.pop("redoc_url", "/redoc")
    config.update({"docs_url": None, "redoc_url": None})

    _app = FastAPI(**config)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 调用 setup_routes 函数，自动添加文档接口
    setup_routes(_app, docs_url, redoc_url)

    # 合并的异常处理器
    @_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logging.warning("Validation Error: %s", exc)
        return JSONResponse(
            content={"msg": "参数校验失败", "code": -1, "data": exc.errors()},
            status_code=400,
        )

    @_app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc: StarletteHTTPException):
        return JSONResponse(
            content={"message": exc.detail},
            status_code=exc.status_code,
        )

    return _app


class Service(BaseModel):
    app: str
    host: str
    port: int

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"  # 不允许未定义的字段

    @classmethod
    def from_config(cls, parser):
        section = "service"
        if parser.has_section(section):
            return cls(
                app=parser.get(section, "app"), host=parser.get(section, "host"), port=parser.getint(section, "port")
            )
        return cls(app="", host="", port=0)  # 默认值


class Fastapi(BaseModel):
    config: dict

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"  # 不允许未定义的字段

    @classmethod
    def from_config(cls, parser):
        section = "fastapi"
        config = {}
        if parser.has_section(section):
            for option in parser.options(section):
                value = parser.get(section, option)
                if value in ["true", "false"]:
                    value = bool(value)
                elif value == "null":
                    value = None
                config[option] = value
        return cls(config=config)


class Mysql(BaseModel):
    ssh_host: str
    ssh_port: int = Field(default=22)
    ssh_user: str
    ssh_password: str
    host: str
    port: int
    username: str
    password: str
    database: str
    db_async: bool = False

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"  # 不允许未定义的字段

    @classmethod
    def from_config(cls, parser):
        section = "mysql"
        if parser.has_section(section):
            return cls(
                ssh_host=parser.get(section, "ssh_host", fallback=""),
                ssh_port=parser.getint(section, "ssh_port", fallback=22),
                ssh_user=parser.get(section, "ssh_user", fallback=""),
                ssh_password=parser.get(section, "ssh_password", fallback=""),
                host=parser.get(section, "host"),
                port=parser.getint(section, "port"),
                username=parser.get(section, "username"),
                password=parser.get(section, "password"),
                database=parser.get(section, "database"),
                db_async=parser.getboolean(section, "async", fallback=False),
            )
        return cls(
            ssh_host="", ssh_user="", ssh_password="", host="", port=0, username="", password="", database=""
        )  # 默认值


class Sqlite(BaseModel):
    path: str = Field(default="/sqlite.db")

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"  # 不允许未定义的字段

    @classmethod
    def from_config(cls, parser):
        section = "sqlite"
        path = cls.path
        if parser.has_section(section) and parser.has_option(section, "path"):
            path = parser.get(section, "path")
        return cls(path=path)


class Settinigs(BaseModel):
    service: Optional[Service] = Field(default=None, description="Service settings")
    fastapi: Optional[Fastapi] = Field(default=None, description="Fastapi settings")
    mysql: Optional[Mysql] = Field(default=None, description="Mysql settings")
    sqlite: Optional[Sqlite] = Field(default=None, description="Sqlite settings")


class BuilderSettings:
    def __init__(self, base_dir, default_setting):
        self.conf_path = os.path.join(base_dir, default_setting)
        self.parser = ConfigParser()
        self.settings: Settinigs = self.mount_configuration()

    def mount_configuration(self) -> Settinigs:
        self.parser.read(self.conf_path, encoding="utf-8")

        settings = Settinigs()
        if self.parser.has_section("service"):
            settings.service = Service.from_config(parser=self.parser)
        if self.parser.has_section("fastapi"):
            settings.fastapi = Fastapi.from_config(parser=self.parser)
        if self.parser.has_section("mysql"):
            settings.mysql = Mysql.from_config(parser=self.parser)
        if self.parser.has_section("sqlite"):
            settings.sqlite = Sqlite.from_config(parser=self.parser)

        return settings
