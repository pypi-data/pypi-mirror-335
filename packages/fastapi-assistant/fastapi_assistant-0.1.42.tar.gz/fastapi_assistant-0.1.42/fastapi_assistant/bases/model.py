from datetime import datetime
from sqlalchemy import Column, TIMESTAMP, text, DateTime, Boolean, Integer, MetaData
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.inspection import inspect


class ModelMixin:
    """
    model 基础类，定义了共用方法
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {"mysql_engine": "InnoDB"}

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class BasicModel(ModelMixin):
    """
    基础模型类，定义了 id 和 create_time 字段
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(TIMESTAMP, default=datetime.now, nullable=True, server_default=text("CURRENT_TIMESTAMP"))


class EnhancedModel(BasicModel):
    """
    增强模型类，增加了 update_time 和 is_deleted 字段
    """

    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间")
    is_deleted = Column(Boolean, default=False, comment="是否删除")


class EnhancedModelV2(BasicModel):
    """
    增强模型类，增加了 update_time 和 delete_time 字段
    """

    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now, comment="更新时间")
    delete_time = Column(DateTime, nullable=True, comment="删除时间")