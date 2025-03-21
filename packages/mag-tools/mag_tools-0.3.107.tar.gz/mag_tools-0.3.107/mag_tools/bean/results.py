from dataclasses import dataclass, field
from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from mag_tools.exception.app_exception import AppException
from mag_tools.model.service_status import ServiceStatus

T = TypeVar('T')


@dataclass
class Results(Generic[T]):
    """
    服务器返回结果包
    """
    code: Optional[ServiceStatus] = field(default=None, metadata={'description': '返回代码'})
    message: Optional[str] = field(default=None, metadata={'description': '错误消息'})
    data: Optional[List[T]] = field(default_factory=list, metadata={'description': '返回数据'})
    total_count: Optional[int] = field(default_factory=list, metadata={'description': '返回数据的个数'})
    timestamp: Optional[datetime] = field(default_factory=datetime.now, metadata={'description': '时间戳'})

    @staticmethod
    def exception(ex: Exception):
        message = str(ex) if ex.args else str(ex.__cause__)
        return Results(code=ServiceStatus.INTERNAL_SERVER_ERROR, message=message)

    @staticmethod
    def success(data: Optional[List[T]] = None):
        return Results(message="OK", data=data)

    @staticmethod
    def fail(message: str):
        return Results(message=message)

    @property
    def is_success(self) -> bool:
        return self.code == ServiceStatus.OK.code

    @property
    def size(self) -> int:
        return len(self.data)

    @property
    def first(self) -> Optional[T]:
        return self.data[0] if self.data and len(self.data) > 0 else None

    def check(self) -> None:
        if not self.is_success:
            raise AppException(self.message)

    def get(self, idx: int) -> Optional[T]:
        self.check()
        return self.data[idx] if idx < self.size else None