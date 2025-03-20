from datetime import datetime, timedelta

from dateutil import parser


class DateUtils:
    @staticmethod
    def float_to_datetime(timestamp: float) -> datetime:
        """
        将浮点数转换为日期时间对象

        :param timestamp: 浮点数，表示自 Unix 纪元以来的秒数
        :return: 日期时间对象
        """
        return datetime(1970, 1, 1) + timedelta(seconds=timestamp)

    @staticmethod
    def to_datetime(date_time_str):
        date_time_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y.%m.%d %H:%M:%S",
            "%Y年%m月%d日 %H时%M分%S秒",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y.%m.%d",
            "%H:%M:%S",
            "%H时%M分%S秒",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y%m%d%H%M%S",
            "%Y%m%d%H%M%S%f",
            "%Y%m%d",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%a %b %d %H:%M:%S %Z %Y",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z"
        ]

        for fmt in date_time_formats:
            try:
                return datetime.strptime(date_time_str, fmt)
            except ValueError:
                continue

        try:
            return parser.parse(date_time_str)
        except ValueError as e:
            return None
