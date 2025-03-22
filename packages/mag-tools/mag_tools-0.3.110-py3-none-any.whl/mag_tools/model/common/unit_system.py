from mag_tools.model.base_enum import BaseEnum


class UnitSystem(BaseEnum):
    METRIC = ("Metric", "米制")
    FIELD = ("Field", "英制")
    LAB = ("Laboratory", "实验室制")
    MESO = ("Microscopic", "微观")
