
from mag_tools.model.base_enum import BaseEnum


class DiskType(BaseEnum):
    """
    磁盘类型枚举类
    """
    SSD = ("SSD", "Solid State Drive")
    HDD = ("HDD", "Hard Disk Drive")
    HYBRID = ("HYBRID", "Hybrid Drive")
    NVME = ("NVME", "Non-Volatile Memory Express")
