import copy
from typing import Optional, Dict, Any

from sqlalchemy.exc import IntegrityError, ArgumentError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

"""仿照django中的 get_or_create 和 update_or_create"""


class FieldError(ArgumentError):
    ...


def resolve_callables(mapping: Dict):
    """
    Generate key/value pairs for the given mapping where the values are
    evaluated if they're callable.
    """
    for k, v in mapping.items():
        yield k, v() if callable(v) else v


def _extract_model_params(model: Any, defaults: Optional[Dict] = None, **kwargs):
    defaults = defaults or {}
    params = copy.deepcopy(kwargs)
    params.update(defaults)
    invalid_params = [param for param in params if not hasattr(model, param)]
    if invalid_params:
        raise FieldError(
            "Invalid field name(s) for model %s: '%s'." % (
                model.__name__, "', '".join(sorted(invalid_params)),
            ))
    return params


async def get_one(db: Session, model: Any, lock: bool = False, **kwargs) -> Any:
    query = db.query(model)
    if lock:
        query = query.with_for_update()
    return query.filter_by(**kwargs).one()


async def _create_object_from_params(db: Session, model: Any, filters: Dict, params: Dict, lock=False):
    obj = model(**params)
    try:
        with db.begin_nested():
            db.add(obj)
            db.flush()
    except IntegrityError:
        db.rollback()
        try:
            obj = await get_one(db, model, lock=lock, **filters)
        except NoResultFound:
            raise
        else:
            return obj, False
    else:
        return obj, True


async def get_or_create(db: Session, model: Any, defaults: Optional[Dict] = None, **kwargs):
    """
    获取一个或更新，存在返回对象，不存在创建，数据只提交了缓存 flush，调用后需要commit
    :param db:
    :param model: 数据模型类
    :param defaults: 模型类属性值
    :param kwargs: 查询条件
    :return: obj，bool
    """
    try:
        return await get_one(db, model, **kwargs), False
    except NoResultFound:
        params = _extract_model_params(model, defaults, **kwargs)
        return await _create_object_from_params(db, model, kwargs, params)


async def update_or_create(db: Session, model: Any, defaults=None, **kwargs):
    """
    更新或创建，存在更新，不存在创建，数据只提交了缓存 flush，调用后需要commit
    :param db:
    :param model: 数据模型类
    :param defaults: 模型类属性值
    :param kwargs: 查询条件
    :return: obj，bool
    :return:
    """
    defaults = defaults or {}
    with db.begin_nested():
        try:
            obj = await get_one(db, model, lock=True, **kwargs)
        except NoResultFound:
            params = _extract_model_params(model, defaults, **kwargs)
            obj, created = await _create_object_from_params(db, model, kwargs, params, lock=True)
            if created:
                return obj, created
        for k, v in resolve_callables(defaults):
            setattr(obj, k, v)
        db.add(obj)
        db.flush()
    return obj, False
