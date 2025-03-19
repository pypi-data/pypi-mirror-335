from datetime import datetime, timedelta

class DateUtils:
    @staticmethod
    def float_to_datetime(timestamp: float) -> datetime:
        """
        将浮点数转换为日期时间对象

        :param timestamp: 浮点数，表示自 Unix 纪元以来的秒数
        :return: 日期时间对象
        """
        return datetime(1970, 1, 1) + timedelta(seconds=timestamp)

if __name__ == '__main__':
    # 示例用法
    timestamp = 1672531199.0  # 示例浮点数
    date_time = DateUtils.float_to_datetime(timestamp)
    print(date_time)
