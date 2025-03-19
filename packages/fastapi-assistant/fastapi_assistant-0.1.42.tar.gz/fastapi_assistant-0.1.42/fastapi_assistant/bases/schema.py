from typing import List, Dict, Any, Optional, Union

from pydantic import BaseModel, Field

from fastapi_assistant.bases.enums import FilterConditionEnum


class BaseSchema(BaseModel):
    """
    基础Schema
    """


class BaseObjSchema(BaseModel):
    """
    基础ObjSchema
    """

    class Config:
        orm_mode = True  # 为模型实例


class RespBaseSchema(BaseSchema):
    """
    基础返回Schema
    """
    code: int = 200  # 返回编号
    message: str = 'SUCCESS'  # 返回消息


class RespDetailSchema(RespBaseSchema):
    """
    详情返回Schema
    """
    detail: dict = Field(default=None, description='详情')


class RespResultSchema(RespBaseSchema):
    result: Any = Field(description='结果')


class RespListSchema(BaseModel):
    """
    列表返回Schema
    """
    page: int = Field(default=0, description='页数')
    size: int = Field(default=0, description='每页大小')
    total: int = Field(default=0, description='数据总条数')
    page_count: int = Field(default=0, description='总页数')
    result: List[Dict] = Field(default=[], description='数据list')


class ListFilterSchema(BaseModel):
    """
    列表参数：过滤条件Schema
    """
    key: str = Field(description='字段名')
    condition: FilterConditionEnum = Field(description='过滤条件')  # 使用Union时，会将数据优先转为第一种类型
    value: Any = Field(default='', description='条件值，condition为in/!in时，value为list, True/False时，value不传')


class ListCustomizeFilterSchema(BaseSchema):
    """
    自定义查询，重新 dao 中 handle_list_customize_filters 方法
    """
    key: str = Field(description='字段名')
    value: Any = Field(default='', description='条件值')


class ListOrderSchema(BaseModel):
    """
    列表参数：排序条件Schema
    """
    key: str = Field(default='', description='字段名')
    clause: Optional[Any] = Field(default=None, description='例如')  # func.CONVERT(text('name USING gbk'))
    condition: str = Field(default='desc', description='排序条件 asc 正序 desc 倒序')


class ListKeySchema(BaseModel):
    """
    列表参数：字段条件Schema
    """
    key: str = Field(description='字段名')
    rename: str = Field(default=None, description='字段名重命名, 为空则不进行重命名')


class ListArgsSchema(BaseModel):
    """
    列表参数Schema
    """
    page: int = Field(default=1, description='当前页码')
    size: int = Field(default=10, description='每页条数')
    filters: List[ListFilterSchema] = Field(default=[], description='过滤条件')
    customize_filters: List[ListCustomizeFilterSchema] = Field(default=[], description='自定义过滤条件')
    orders: List[ListOrderSchema] = Field(default=[], description='排序条件')  # 排序条件
    keys: List[ListKeySchema] = Field(default=[], description='重定义字段')
