# -*- encoding: utf-8 -*-
import string


def GetDic():
    """
    获取数字和字母的对应关系，生成一部字典，键为数字，值为字母组合。

    该函数的主要功能是创建一部字典，其中：
    - 键是从 0 开始的整数；
    - 值是大写字母或大写字母的组合（如 "A", "B", ..., "AA", "AB" 等）。

    :return: dict
        返回一部字典，包含数字与字母组合的映射关系。
    """
    zm = string.ascii_uppercase  # 获取所有大写字母 A-Z
    cellDic = {}  # 初始化存储数字与字母映射关系的字典
    s = 0  # 初始化计数器，用于生成字典的键

    # 遍历所有单个大写字母，建立初步的数字与字母的映射关系
    for i in zm:
        cellDic[s] = str(i).upper()
        s += 1  # 每次循环后递增计数器

    # 遍历两个大写字母的组合，扩展字典的映射关系
    for i in zm:
        for m in zm:
            k = str(i) + str(m)  # 生成两个字母的组合
            cellDic[s] = k.upper()  # 将组合添加到字典中
            s += 1  # 每次循环后递增计数器

    return cellDic  # 返回最终生成的字典

