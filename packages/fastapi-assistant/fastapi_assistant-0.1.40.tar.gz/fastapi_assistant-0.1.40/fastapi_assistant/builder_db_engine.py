from collections.abc import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


from fastapi_assistant.builder_api import Settinigs


class BuilderDbEngine:
    def __init__(self, engine_: Engine = None, settings_: Settinigs = None, db_config: dict = None, **kwargs):
        self.db_async = False
        self.engine = self.generate_engine(engine_, settings_, db_config, **kwargs)


    def generate_url(
        self,
        settings: Settinigs = None,
        db_config: dict = None,
    ):
        """
        生成db url, 优先级 db_config > settings > 默认sqlit3
        :param settings: 读取的ini配置文件
        :param db_config: 数据库配置
        :return:
        """
        if db_config:
            db_host = db_config.get("host", "")
            db_port = db_config.get("port", "")
            if db_config.get("ssh_host"):
                tunnel = get_ssh_tunnel(
                    db_host,
                    db_port,
                    db_config.get("ssh_host", ""),
                    db_config.get("ssh_port", ""),
                    db_config.get("ssh_user", ""),
                    db_config.get("ssh_password", ""),
                )
                db_host = "127.0.0.1"
                db_port = tunnel.local_bind_port
            self.db_async = db_config.get("db_async", False)
            return URL(
                drivername="mysql+aiomysql" if self.db_async else "mysql+pymysql",
                username=db_config.get("username", ""),
                password=db_config.get("password", ""),
                host=db_host,
                port=db_port,
                database=db_config.get("database", ""),
            )
        if settings and settings.mysql:
            mysql = settings.mysql
            host = mysql.host
            port = mysql.port
            if mysql.ssh_host:
                tunnel = get_ssh_tunnel(
                    mysql.host,
                    mysql.port,
                    mysql.ssh_host,
                    mysql.ssh_port,
                    mysql.ssh_user,
                    mysql.ssh_password,
                )
                host = "127.0.0.1"
                port = tunnel.local_bind_port
            self.db_async = mysql.db_async
            return URL(
                drivername="mysql+aiomysql" if self.db_async else "mysql+pymysql",
                username=mysql.username,
                password=mysql.password,
                host=host,
                port=port,
                database=mysql.database,
            )
        path = settings.Sqlit.path if hasattr(settings, "Sqlit") else "/sqlit3.db"
        return "sqlite://{}?check_same_thread=False".format(path)

    def generate_engine(self, _engine: Engine = None, settings_: Settinigs = None, db_config: dict = None, **kwargs):
        if _engine:
            return _engine
        db_url = self.generate_url(settings_, db_config)
        if self.db_async:
            return create_async_engine(db_url, **kwargs)
        return create_engine(db_url, **kwargs)

    def get_base(self, **kwargs):
        return declarative_base(bind=self.engine, **kwargs)

    def get_sessionmaker(self) -> sessionmaker:
        if self.db_async:
            return sessionmaker(class_=AsyncSession, autocommit=False, autoflush=False, bind=self.engine)
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_database(self):
        db = self.get_sessionmaker()()
        try:
            yield db
        finally:
            db.close()

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.get_sessionmaker()() as session:
            yield session


def get_ssh_tunnel(host: str, port: int, ssh_host: str, ssh_port: int, ssh_user: str, ssh_password: str):
    """
    创建SSH隧道
    :param host: 数据库地址
    :param port: 数据库端口
    :param ssh_host: ssh地址
    :param ssh_port: ssh端口
    :param ssh_user: ssh用户名
    :param ssh_password: ssh密码
    :return: _description_
    """
    from sshtunnel import SSHTunnelForwarder

    tunnel = SSHTunnelForwarder(
        (ssh_host, ssh_port), ssh_username=ssh_user, ssh_password=ssh_password, remote_bind_address=(host, port)
    )
    tunnel.start()
    return tunnel
