from typing import Optional

from fastapi import HTTPException


class ExceptionFactory(HTTPException):
    status_code = 400
    detail = '异常'

    def __init__(self, detail: Optional[str] = None, status_code: int = None, ) -> None:
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        super(ExceptionFactory, self).__init__(self.status_code, self.detail)


class CreateException(ExceptionFactory):
    status_code = 500
    detail = '创建异常'


class NotFoundException(ExceptionFactory):
    status_code = 404
    detail = '资源不存在'


class UpdateException(ExceptionFactory):
    status_code = 500
    detail = '更新失败'


class DeleteException(ExceptionFactory):
    status_code = 500
    detail = '删除失败'


class FileTypeException(ExceptionFactory):
    detail = '上传文件类型错误'