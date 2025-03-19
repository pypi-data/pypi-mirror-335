from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi_assistant.bases.model import EnhancedModel
from fastapi_assistant.bases.schema import ListArgsSchema, ListCustomizeFilterSchema, ListFilterSchema, ListOrderSchema
from fastapi_assistant.core.sqlalchemy_asyncio import get_or_create, update_or_create


class AsyncDao(object):
    Model = EnhancedModel

    def __init__(self, operator_id=0):
        self.operator_id = operator_id

    def base_filters(self) -> List:
        """
        基础的过滤条件，如果软删除字段修改，需要重写
        """
        return [~self.Model.is_deleted] if hasattr(self.Model, "is_deleted") else []

    @staticmethod
    async def create(db: AsyncSession, obj: EnhancedModel, is_commit: bool = True):
        """
        创建一条记录
        :param db:
        :param obj:
        :param is_commit:
        :return:
        """
        try:
            db.add(obj)
            await db.flush()
        except Exception as e:
            if is_commit:
                await db.rollback()
            raise e
        if is_commit:
            await db.commit()

    async def dict_create(self, db: AsyncSession, object_dict: Dict[str, Any], is_commit: bool = True) -> EnhancedModel:
        model = self.Model(**object_dict)
        try:
            db.add(model)
            await db.flush()
        except Exception as e:
            if is_commit:
                await db.rollback()
            raise e  # 重新抛出异常
        if is_commit:
            await db.commit()  # 提交事务
            await db.refresh(model)
        return model

    async def get_or_create(
        self, db: AsyncSession, defaults=None, is_commit: bool = True, **kwargs
    ) -> Tuple[EnhancedModel, bool]:
        """
        获取一个或创建一个 defaults
        :param db:
        :param defaults: 扩充条件
        :param is_commit: 是否提交
        :param kwargs: 查询条件
        :return:
        """
        obj, created = await get_or_create(db, self.Model, defaults, **kwargs)
        if is_commit:
            try:
                await db.commit()
                await db.refresh(obj)
            except IntegrityError:
                # 创建遇到唯一索引
                await db.rollback()
                return await get_or_create(db, self.Model, defaults, **kwargs)
        return obj, created

    async def update_or_create(
        self, db: AsyncSession, defaults=None, is_commit=True, **kwargs
    ) -> Tuple[EnhancedModel, bool]:
        """
        更新或创建一个
        :param db:
        :param defaults: 更新内容
        :param is_commit: 是否提交
        :param kwargs: 查询条件
        :return:
        """
        obj, created = await update_or_create(db, self.Model, defaults, **kwargs)
        if is_commit:
            await db.commit()
            await db.refresh(obj)
        return obj, created

    async def get(self, db: AsyncSession, pk: int) -> EnhancedModel:
        """
        获取一条数据
        :param db:
        :param pk: id
        :return: 返回这个模型数据
        """
        filters = self.base_filters()
        filters.append(self.Model.id == pk)
        result = await db.execute(select(self.Model).filter(*filters))
        return result.scalars().first()

    async def update(self, db: AsyncSession, pk: int, update_data: dict, is_commit: bool = True):
        """
        更新一条数据
        :param db:
        :param pk:
        :param update_data:
        :param is_commit: 是否提交
        """
        filters = self.base_filters()
        filters.append(self.Model.id == pk)
        try:
            await db.execute(self.Model.__table__.update().where(*filters).values(update_data))
            await db.flush()
        except Exception as e:
            if is_commit:
                await db.rollback()
            raise e
        if is_commit:
            await db.commit()

    async def delete(self, db: AsyncSession, pk: int, is_commit: bool = True):
        """
        删除一条数据，定义了 is_deleted 进行软删除，否则真删除
        :param db:
        :param pk: id
        :param is_commit: 是否提交
        """
        filters = self.base_filters()
        try:
            if filters:
                filters.append(self.Model.id == pk)
                await db.execute(self.Model.__table__.update().where(*filters).values(is_deleted=True))
            else:
                await db.execute(self.Model.__table__.delete().where(self.Model.id == pk))
            await db.flush()
        except Exception as e:
            if is_commit:
                await db.rollback()
            raise e
        if is_commit:
            await db.commit()

    async def count(self, db: AsyncSession, args: ListArgsSchema) -> int:
        """
        获取记录数
        :param db:
        :param args:
        :return:
        """
        filters = self.process_filters(args)
        result = await db.execute(select(func.count()).select_from(self.Model).filter(*filters))
        return result.scalar()

    def process_filters(self, args: ListArgsSchema) -> List[Any]:
        """
        处理查询条件
        """
        filters = self.base_filters()
        filters.extend(self.handle_list_filters(args.filters))
        filters.extend(self.handle_list_customize_filters(args.customize_filters))
        return filters

    async def list(self, db: AsyncSession, args: ListArgsSchema) -> Tuple[int, List[EnhancedModel]]:
        """
        数据列表
        :param db:
        :param args: 聚合参数，详见：ListArgsSchema
        :return: 返回数据列表结构，详见：RespListSchema
        :param args:
        :return:
        """
        filters = self.process_filters(args)
        # 执行：数据检索
        query = select(self.Model).filter(*filters)
        count_query = select(func.count()).select_from(self.Model).filter(*filters)
        count_result = await db.execute(count_query)
        count = count_result.scalar()

        obj_list = []
        if count > 0:
            orders = self.handle_list_orders(args.orders)
            for order in orders:
                query = query.order_by(order)
            query = query.offset((args.page - 1) * args.size).limit(args.size)
            result = await db.execute(query)
            obj_list = result.scalars().all()
        return count, obj_list

    def handle_list_filters(self, args_filters: Optional[List[ListFilterSchema]]) -> List:
        """
        查询条件组装
        :param args_filters:
        :return:
        """
        filters = []
        if args_filters:
            for item in args_filters:
                if hasattr(self.Model, item.key):
                    attr = getattr(self.Model, item.key)
                    filters.append(item.condition.desc(attr, item.value))
        return filters

    def handle_list_customize_filters(self, args_filters: List[ListCustomizeFilterSchema]) -> List:
        """
        负责的一些负责的查询，自己定义
        :param args_filters:
        :return:
        """
        ...
        return []

    def handle_list_orders(self, args_orders: Optional[List[ListOrderSchema]]) -> List:
        """
        处理list接口传入的排序条件
        :param args_orders: 传入排序条件
        :return: 转换后的sqlalchemy排序条件
        """
        orders = []
        if args_orders:
            for item in args_orders:
                if item.clause is not None:
                    attr = item.clause
                elif hasattr(self.Model, item.key):
                    attr = getattr(self.Model, item.key)
                else:
                    continue
                if item.condition == "desc":
                    orders.append(attr.desc())
                elif item.condition == "asc":
                    orders.append(attr)
                elif item.condition == "rand":  # 随机排序
                    orders.append(func.rand())
        return orders

    async def list_by_filters(self, db: AsyncSession, criterion: List) -> Tuple[int, List[EnhancedModel]]:
        """
        根据查询条件list 进行查询
        :param db:
        :param args:
        :return:
        """
        criterion.extend(self.base_filters())
        result = await db.execute(select(self.Model).filter(*criterion))
        return result.scalars().all()
