from mag_tools.model.base_enum import BaseEnum


class DimensionType(BaseEnum):
    DX = ('dx', 'Dimension X')  # 维度X
    DY = ('dy', 'Dimension Y')  # 维度Y
    DZ = ('dz', 'Dimension Z')  # 维度Z


if __name__ == '__main__':
    # 示例用法
    print(DimensionType.DX.code)  # 输出: dx
    print(DimensionType.DY.desc)  # 输出: Dimension Y
    print(DimensionType.get_by_code('dx').desc)  # 输出: Dimension X
