from fastapi import Query
from sqlalchemy.orm import query


class Pagination:
    """分页类"""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="页数"),
        size: int = Query(10, gt=0, description="每页个数"),
    ):
        self.page = page
        self.size = size

    @property
    def offset(self) -> int:
        """
        计算分页的偏移量
        """
        return (self.page - 1) * self.size

    def apply_pagination(self, query: query.Query) -> query.Query:
        """
        应用分页到查询对象上
        :param query: SQLAlchemy 查询对象
        :return: 带有分页的查询对象
        """
        query = self.apply_sorting(query)
        return query.offset(self.offset).limit(self.size)
