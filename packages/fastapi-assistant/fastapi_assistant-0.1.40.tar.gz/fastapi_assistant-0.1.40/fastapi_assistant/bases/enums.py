from enum import Enum
from typing import Optional, Any


class BasicEnum(Enum):
    def __new__(cls, key, desc):
        obj = object.__new__(cls)
        obj.key = obj._value_ = key
        obj.desc = desc
        return obj

    @classmethod
    def get_enum(cls, value) -> Optional[Any]:
        try:
            return cls(value)
        except ValueError:
            return None

    @classmethod
    def get_enum_by_desc(cls, desc) -> Optional[Any]:
        for item in cls:
            if item.desc == desc:
                return item
        return None

    @classmethod
    def choices(cls):
        return [(item.key, item.desc) for item in cls]

    @classmethod
    def items(cls) -> list:
        return [item.key for item in cls]


class FilterConditionEnum(BasicEnum):
    equal = '=', lambda attr, value: attr == value
    not_equal = '!=', lambda attr, value: attr != value
    lt = '<', lambda attr, value: attr < value
    gt = '>', lambda attr, value: attr > value
    lte = '<=', lambda attr, value: attr <= value
    gte = '>=', lambda attr, value: attr >= value
    like = 'like', lambda attr, value: attr.like(f'%{value}%')
    in_ = 'in', lambda attr, value: attr.in_(value)
    not_in_ = '!in', lambda attr, value: ~attr.in_(value)
    is_null = 'null', lambda attr, _: attr.is_(None)
    is_not_null = '!null', lambda attr, _: ~attr.is_(None)
    between = 'between', lambda attr, value: attr.between(value[0], value[1])
    true = True, lambda attr, _: attr  # True、False 用于 sqlalchemy 定义的 Boolean 类型
    false = False, lambda attr, _: ~attr
