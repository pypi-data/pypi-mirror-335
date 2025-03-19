import logging
from fastapi_assistant.bases import FilterConditionEnum
from pydantic import BaseModel
from typing import Dict, Optional, Any, List, Type, ClassVar
import sqlalchemy
from sqlalchemy.orm import Session, query
from packaging.version import Version
from importlib.metadata import version


class QueryField:
    """
    定义一个用于SQLAlchemy过滤的字段。
    """  

    def __init__(
        self,
        field_name: str,
        lookup_expr: Optional[FilterConditionEnum] = FilterConditionEnum.equal,
        method: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        """_summary_: 初始化一个用于SQLAlchemy过滤的字段。

        :param field_name: 表字段名字
        :param lookup_expr: 过滤条件, defaults to FilterConditionEnum.equal
        :param method: 指定过滤方法, defaults to None
        :param value: 过滤的值, defaults to None
        """
        self.field_name = field_name
        self.lookup_expr = lookup_expr
        self.method = method
        self.value = value

    def get_filter(self, model: Type[sqlalchemy.Table]) -> Optional[Any]:
        """_summary_: 根据定义的过滤条件，生成SQLAlchemy过滤表达式。

        :param model: _description_
        :return: _description_
        """
        try:
            if self.value is None:
                logging.warning(f"过滤字段 '{self.field_name}' 的值为空")
                return None
            attr = getattr(model, self.field_name, None)
            if attr is None:
                logging.warning(f"模型 '{model.__name__}' 中没有字段 '{self.field_name}'")
                return None
            return self.lookup_expr.desc(attr, self.value)
        except Exception as e:
            logging.error(f"获取过滤字段 '{self.field_name}' 时发生错误: {e}")
        return None


class DefaultMeta:
    """
    提供默认的 Meta 类，防止子类未定义 Meta 类时出现问题。
    """

    model: Optional[Type[sqlalchemy.Table]] = None
    fields: List[str] = []


ADDITIONAL_QUERY_NAME_IN_FIELD = "query"

IS_PYDANTIC_VERSION_9_OR_HIGHER = Version(version("pydantic")) > Version("1.9.0")  # 判断是否是pydantic版本大于等于1.9.0


class FilterSet(BaseModel):
    """
    过滤器基类，处理所有定义的过滤字段并生成SQLAlchemy过滤条件。
    """

    Meta: ClassVar[Type[DefaultMeta]] = DefaultMeta  # 使用默认 Meta 类
    _query_fields: Dict[str, QueryField] = {}

    def __init__(self, **data: Any) -> None:
        if not hasattr(self.Meta, "model") or not self.Meta.model:
            raise ValueError(f"过滤类 '{self.__class__.__name__}' 必须定义 Meta 类，并设置 model 属性")
        if not hasattr(self.Meta, "fields") or not self.Meta.fields:
            raise ValueError(f"过滤类 '{self.__class__.__name__}' 必须定义 Meta 类，并设置 fields 属性")
        super().__init__(**data)
        self.get_query_fields()

    def get_query_fields(self) -> Dict[str, QueryField]:
        """_summary_: 获取所有定义的查询字段，并返回一个字典。

        :return: _description_
        """
        # fields = self.model_fields if IS_PYDANTIC_VERSION_9_OR_HIGHER else self.__fields__
        having_model_fields = hasattr(self, "model_fields")
        fields = self.model_fields if having_model_fields else self.__fields__

        for field_name, field in fields.items():
            extra = field.json_schema_extra if having_model_fields else field.field_info.extra
            query = extra.get(ADDITIONAL_QUERY_NAME_IN_FIELD)
            if isinstance(query, QueryField):
                self._query_fields[field_name] = query
            else:
                logging.warning(f"过滤类 '{self.__class__.__name__}' 中字段 '{field_name}' 没有定义查询字段")

    def get_filters(self) -> List[Any]:
        """_summary_: 获取所有定义的过滤条件，并返回一个SQLAlchemy过滤表达式列表。

        :raises ValueError: 如果 Meta 类未定义或未设置 model 或 fields 属性，则抛出 ValueError 异常
        :return: SQLAlchemy过滤表达式列表
        """
        _filters = []
        for field_name in self.Meta.fields:
            if not hasattr(self, field_name):
                logging.warning(f"过滤类 '{self.__class__.__name__}' 中定义了字段 '{field_name}' 但未定义这个属性")
                continue
            field_value = getattr(self, field_name, None)
            if field_value is None:
                continue
            filter_field = self._query_fields.get(field_name)
            if filter_field is None:
                logging.warning(f"过滤类 '{self.__class__.__name__}' 中字段 '{field_name}' 没有定义查询字段")
                continue
            filter_condition = self._apply_filter_method(filter_field, field_value)
            if filter_condition is not None:
                _filters.append(filter_condition)
        return _filters

    def _apply_filter_method(self, filter_field: QueryField, field_value: Any) -> Optional[Any]:
        """_summary_: 应用过滤器的方法或直接生成过滤表达式。

        :param filter_field: 过滤器字段对象
        :param field_value: 过滤字段的值
        :return: SQLAlchemy过滤表达式
        """
        if filter_field.method:
            filter_function = getattr(self, filter_field.method, None)
            if not filter_function:
                logging.warning(
                    f"过滤类 '{self.__class__.__name__}' 中字段 '{filter_field.field_name}' 指定的方法 '{filter_field.method}' 不存在"
                )
                return None
            return filter_function(field_value)
        else:
            filter_field.value = field_value
            return filter_field.get_filter(self.Meta.model)

    def apply_filters(self, db: Session, query: Optional[query.Query] = None) -> query.Query:
        """_summary_: 将过滤条件应用到一个SQLAlchemy查询对象上。如果没有提供查询对象，则创建一个。

        :param db: SQLAlchemy数据库会话
        :param query: SQLAlchemy查询对象，默认为 None
        :raises ValueError: 如果 Meta 类未定义模型，则抛出 ValueError 异常
        :return: SQLAlchemy查询对象
        """
        if query is None:
            if self.Meta.model is None:
                raise ValueError(f"过滤类 '{self.__class__.__name__}' 的 Meta 类未定义模型")
            query = db.query(self.Meta.model)

        filters = self.get_filters()
        if filters:
            query = query.filter(*filters)

        return query
