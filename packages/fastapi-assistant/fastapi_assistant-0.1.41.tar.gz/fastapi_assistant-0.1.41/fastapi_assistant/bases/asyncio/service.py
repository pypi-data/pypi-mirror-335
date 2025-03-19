import math
from enum import Enum
from logging import error
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_assistant.bases.asyncio.dao import AsyncDao
from fastapi_assistant.bases.model import EnhancedModel
from fastapi_assistant.bases.schema import ListArgsSchema, ListKeySchema, RespListSchema
from fastapi_assistant.core import CreateException, NotFoundException, UpdateException


class AsyncService:
    """
    Base(基础)服务，用户被继承
    CRUD基础服务类，拥有基本方法，可直接被继承使用
    """

    Model = EnhancedModel
    dao = AsyncDao()

    def __init__(self, operator_id: int = 0):
        self.operator_id = operator_id

    async def create(self, db: AsyncSession, schema: Dict) -> EnhancedModel:
        """
        创建一条数据
        :param db: 数据库会话
        :param schema: 创建所需的字段
        :return: 创建的模型实例
        """
        model = self.Model()
        self.schema_to_model(schema, model)
        try:
            await self.dao.create(db, model)
        except Exception as e:
            error(f"写入 {self.Model.__tablename__} 错误: {e} schema: {schema}")
            raise CreateException()
        return model

    async def partial_update(self, db: AsyncSession, pk: int, updates_data: Dict) -> EnhancedModel:
        """
        局部更新
        :param db: 数据库会话
        :param pk: 要更新的记录 ID
        :param updates_data: 更新的字段
        :return: 更新后的模型实例
        """
        obj = await self.dao.get(db, pk)
        if not obj:
            raise NotFoundException()
        try:
            await self.dao.update(db, pk, updates_data)
            await db.refresh(obj)
        except Exception as e:
            error(f"局部更新 {self.Model.__tablename__} 错误: {e} 更新数据: {updates_data}")
            raise UpdateException()
        return obj

    async def update(self, db: AsyncSession, schema: Dict) -> EnhancedModel:
        """
        更新一条数据
        :param db: 数据库会话
        :param schema: 更新所需的字段
        :return: 更新后的模型实例
        """
        obj = await self.dao.get(db, schema["id"])
        if not obj:
            raise NotFoundException()
        try:
            await self.dao.update(db, schema["id"], dict(schema))
            await db.refresh(obj)
        except Exception as e:
            error(f"更新 {self.Model.__tablename__} 错误: {e} schema: {schema}")
            raise UpdateException()
        return obj

    async def delete(self, db: AsyncSession, pk: int):
        """
        删除单条数据
        :param db: 数据库会话
        :param pk: 要删除的记录 ID
        """
        try:
            await self.dao.delete(db, pk)
        except Exception as e:
            error(f"软删除 {self.Model.__tablename__} 错误: {e} pk: {pk}")
            raise UpdateException()

    async def get(self, db: AsyncSession, pk: int) -> EnhancedModel:
        """
        读取单条数据
        :param db: 数据库会话
        :param pk: 要读取的记录 ID
        :return: 模型实例
        """
        obj = await self.dao.get(db, pk)
        if not obj:
            raise NotFoundException()
        return obj

    async def count(self, db: AsyncSession, args: ListArgsSchema) -> int:
        """
        获取记录数
        :param db: 数据库会话
        :param args: 过滤和分页参数
        :return: 记录总数
        """
        return await self.dao.count(db, args)

    async def list(self, db: AsyncSession, args: ListArgsSchema) -> RespListSchema:
        """
        读取多条数据
        :param db: 数据库会话
        :param args: 过滤和分页参数
        :return: 响应列表
        """
        count, obj_list = await self.dao.list(db, args)
        resp = RespListSchema(
            page=args.page,
            size=args.size,
            total=count,
            page_count=math.ceil(count / args.size),  # 计算总页数
            result=self.handle_list_keys(args.keys, obj_list),  # 处理list
        )
        return resp

    @staticmethod
    def schema_to_model(schema: Dict, model: EnhancedModel):
        """
        从schema，给model赋值
        :param schema: model对应的schema
        :param model: model的实体
        """
        for key, value in schema.items():
            model.__setattr__(key, value.value if isinstance(value, Enum) else value)

    def handle_list_keys(self, args_keys: Optional[List[ListKeySchema]], obj_list: List[EnhancedModel]) -> List[dict]:
        """
        处理list返回数据，根据传入参数keys进行过滤
        :param args_keys: 传入过滤字段
        :param obj_list: 模型列表
        :return: 转换后的list数据，数据转为dict类型
        """
        keys = [item for item in args_keys if hasattr(self.Model, item.key)] if args_keys else []

        return [
            {item.rename if item.rename else item.key: getattr(obj, item.key) for item in keys}
            if keys
            else obj.to_dict()
            for obj in obj_list
        ]
