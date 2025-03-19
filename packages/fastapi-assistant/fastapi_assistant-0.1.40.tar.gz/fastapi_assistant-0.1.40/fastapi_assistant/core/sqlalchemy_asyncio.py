import copy
from typing import Optional, Dict, Any

from sqlalchemy.exc import IntegrityError, ArgumentError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import MultipleResultsFound


class FieldError(ArgumentError): ...


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
            "Invalid field name(s) for model %s: '%s'."
            % (
                model.__name__,
                "', '".join(sorted(invalid_params)),
            )
        )
    return params


async def get_one(db: AsyncSession, model: Any, lock: bool = False, **kwargs) -> Any:
    query = select(model).filter_by(**kwargs)
    if lock:
        query = query.with_for_update()
    result = await db.execute(query)
    return result.scalars().one()


async def _create_object_from_params(db: AsyncSession, model: Any, filters: Dict, params: Dict, lock=False):
    obj = model(**params)
    try:
        async with db.begin_nested():
            db.add(obj)
            await db.flush()
    except IntegrityError:
        await db.rollback()
        try:
            obj = await get_one(db, model, lock=lock, **filters)
        except (NoResultFound, MultipleResultsFound):
            raise
        else:
            return obj, False
    else:
        return obj, True


async def get_or_create(db: AsyncSession, model: Any, defaults: Optional[Dict] = None, **kwargs):
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
    except (NoResultFound, MultipleResultsFound):
        params = _extract_model_params(model, defaults, **kwargs)
        return await _create_object_from_params(db, model, kwargs, params)


async def update_or_create(db: AsyncSession, model: Any, defaults=None, **kwargs):
    """
    更新或创建，存在更新，不存在创建，数据只提交了缓存 flush，调用后需要commit
    :param db:
    :param model: 数据模型类
    :param defaults: 模型类属性值
    :param kwargs: 查询条件
    :return: obj，bool
    """
    defaults = defaults or {}
    async with db.begin_nested():
        try:
            obj = await get_one(db, model, lock=True, **kwargs)
        except (NoResultFound, MultipleResultsFound):
            params = _extract_model_params(model, defaults, **kwargs)
            obj, created = await _create_object_from_params(db, model, kwargs, params, lock=True)
            if created:
                return obj, created
        for k, v in resolve_callables(defaults):
            setattr(obj, k, v)
        db.add(obj)
        await db.flush()
    return obj, False
