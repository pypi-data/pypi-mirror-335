from datetime import datetime
from typing import Generic, TypeVar, Optional

from mag_tools.exception.app_exception import AppException
from mag_tools.model.service_status import ServiceStatus

T = TypeVar('T')

class Result(Generic[T]):
    def __init__(self, status: Optional[ServiceStatus] = ServiceStatus.OK, code: Optional[ServiceStatus] = ServiceStatus.OK,
                 message: Optional[str] = None, data: Optional[T] = None):
        self.status = (status if status else ServiceStatus.OK).code
        self.code = (code if code else ServiceStatus.OK).code
        self.message = message if message else status.desc if status else None
        self.timestamp = datetime.now()
        self.data = data

    @staticmethod
    def exception(ex: Exception) -> 'Result':
        message = str(ex) if ex.args else str(ex.__cause__)
        return Result(status=ServiceStatus.INTERNAL_SERVER_ERROR, code=ServiceStatus.INTERNAL_SERVER_ERROR, message=message)

    @staticmethod
    def success(data: Optional[T] = None) -> 'Result':
        return Result(message="OK", data=data)

    @staticmethod
    def fail(message: str) -> 'Result':
        return Result(code=ServiceStatus.INTERNAL_SERVER_ERROR, message=message)

    @staticmethod
    def unauthorized(message: str) -> 'Result':
        return Result(status=ServiceStatus.UNAUTHORIZED, code=ServiceStatus.UNAUTHORIZED, message=message)

    @staticmethod
    def forbidden(message: str) -> 'Result':
        return Result(status=ServiceStatus.FORBIDDEN, code=ServiceStatus.FORBIDDEN, message=message)

    def is_success(self) -> bool:
        return self.status == ServiceStatus.OK and self.code == ServiceStatus.OK

    def check(self) -> None:
        if not self.is_success():
            raise AppException(self.message)

    def data(self) -> Optional[T]:
        return self.data