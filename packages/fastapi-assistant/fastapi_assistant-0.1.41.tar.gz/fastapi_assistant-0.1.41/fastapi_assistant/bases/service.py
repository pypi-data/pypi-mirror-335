import math
from enum import Enum
from logging import error
from typing import Optional, List

from sqlalchemy.orm import Session

from fastapi_assistant.bases.model import EnhancedModel
from fastapi_assistant.bases.dao import BasicDao
from fastapi_assistant.bases.schema import ListArgsSchema, RespListSchema, ListKeySchema
from fastapi_assistant.core import NotFoundException, CreateException, UpdateException


class BasicService(object):
    """
    Base(基础)服务，用户被继承
    CRUD基础服务类，拥有基本方法，可直接被继承使用
    """
    Model = EnhancedModel
    dao = BasicDao()

    def __init__(self, operator_id: int = 0):
        self.operator_id = operator_id

    async def create(self, db: Session, schema) -> Model:
        """
        创建一条数据
        :param db:
        :param schema:
        :return:
        """
        model = self.Model()
        self.schema_to_model(schema, model)
        try:
            await self.dao.create(db, model)
        except Exception as e:
            error('写入 {} error:{} schema:{}'.format(self.Model.__tablename__, e, dict(schema)))
            raise CreateException()
        return model

    async def partial_update(self, db: Session, pk: int, updates_data: dict) -> Model:
        """
        局部更新
        :param db:
        :param pk: id
        :param updates_data: 更新的字段
        :return:
        """
        obj = await self.dao.get(db, pk)
        if not obj:
            raise NotFoundException()
        try:
            await self.dao.update(db, pk, updates_data)
        except Exception as e:
            error('局部更新 {} error:{} updates_data:{}'.format(self.Model.__tablename__, e, updates_data))
            raise UpdateException()
        return obj

    async def update(self, db: Session, schema) -> Model:
        """
        更新一条数据
        :param db:
        :param schema:
        :return:
        """
        obj = await self.dao.get(db, schema.id)
        if not obj:
            raise NotFoundException()
        try:
            await self.dao.update(db, schema.id, dict(schema))
        except Exception as e:
            error('更新 {} error:{} schema:{}'.format(self.Model.__tablename__, e, dict(schema)))
            raise UpdateException()
        return obj

    async def delete(self, db: Session, pk: int):
        """
        删除单条数据
        :param db:
        :param pk: id
        :return:
        """
        try:
            await self.dao.delete(db, pk)
        except Exception as e:
            error('软删除 {} error:{} pk:{}'.format(self.Model.__tablename__, e, pk))
            raise UpdateException()

    async def get(self, db: Session, pk: int) -> Model:
        """
        读取单条数据
        :param db:
        :param pk: id
        :return:
        """
        obj = await self.dao.get(db, pk)
        if not obj:
            raise NotFoundException()
        return obj

    async def count(self, db: Session, args: ListArgsSchema) -> int:
        """
        获取记录数
        :param db:
        :param args:
        :return:
        """
        return await self.dao.count(db, args)

    async def list(self, db: Session, args: ListArgsSchema) -> RespListSchema:
        """
        读取多条数据
        :param db:
        :param args:
        :return:
        """
        count, obj_list = await self.dao.list(db, args)
        resp = RespListSchema()
        resp.page = args.page
        resp.size = args.size
        resp.total = count
        resp.page_count = math.ceil(count / args.size)  # 计算总页数
        resp.result = self.handle_list_keys(args.keys, obj_list)  # 处理list
        return resp

    @staticmethod
    def schema_to_model(schema, model):
        """
        从schema，给model赋值，
        :param schema: model对应的schema，详见schema中对应的实体
        :param model: model的实体
        :return: 是否创建成功，创建成功则附加数据id
        """
        for (key, value) in schema:
            if isinstance(value, Enum):
                value = value.value
            model.__setattr__(key, value)

    def handle_list_keys(self, args_keys: Optional[List[ListKeySchema]], obj_list: List[Model]) -> List[dict]:
        """
        处理list返回数据，根据传入参数keys进行过滤
        :param args_keys: 传入过滤字段
        :param obj_list:
        :return: 转换后的list数据，数据转为dict类型
        """
        keys = []

        if args_keys:
            for item in args_keys:
                if hasattr(self.Model, item.key):
                    keys.append(item)

        resp_list = []

        for obj in obj_list:
            dict_1 = obj.to_dict()
            # 判断：keys存在，不存在则返回所有字段
            if keys:
                dict_2 = {}
                for item in keys:
                    if item.rename:
                        dict_2[item.rename] = dict_1[item.key]
                    else:
                        dict_2[item.key] = dict_1[item.key]
            else:
                dict_2 = dict_1

            resp_list.append(dict_2)

        return resp_list
