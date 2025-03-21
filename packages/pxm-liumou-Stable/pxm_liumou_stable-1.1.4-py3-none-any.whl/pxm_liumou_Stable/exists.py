# -*- encoding: utf-8 -*-
from pathlib import Path
from loguru import logger


def _exists(file, flist=None):
    """
    检查文件是否存在、是否为有效文件，并验证文件格式是否符合要求。

    参数:
        file (str): 文件路径。
        flist (list): 允许的文件格式列表，默认为 ["xls", "xlsx", "et"]。

    返回:
        bool: 如果文件存在且格式有效，返回 True；否则返回 False。
    """
    # 如果未提供文件格式列表，则使用默认值 ["xls", "xlsx", "et"]
    if flist is None:
        flist = ["xls", "xlsx", "et"]

    # 将文件路径转换为 Path 对象以便进行操作
    path = Path(file)

    # 检查文件是否存在，如果不存在则记录警告日志并返回 False
    if not path.exists():
        logger.warning(f"文件不存在: {sanitize_log_path(file)}")
        return False

    # 检查路径是否为文件，如果不是文件则记录警告日志并返回 False
    if not path.is_file():
        logger.warning(f"该对象不是文件: {sanitize_log_path(file)}")
        return False

    # 提取文件的扩展名并检查是否在允许的文件格式列表中
    file_format = get_file_extension(path)
    if file_format in flist:
        return True

    # 如果文件格式不符合要求，记录错误日志并返回 False
    logger.error(f"不支持的文件格式: {file_format}")
    return False

def get_file_extension(path):
    """
    提取文件的扩展名（不包括点）。

    参数:
        path (Path): 文件路径对象。

    返回:
        str: 文件扩展名（小写），如果没有扩展名则返回空字符串。
    """
    return path.suffix.lstrip('.').lower()

def sanitize_log_path(file):
    """
    对日志中的文件路径进行脱敏处理，避免暴露敏感信息。

    参数:
        file (str): 文件路径。

    返回:
        str: 脱敏后的文件路径。
    """
    # 示例：仅保留文件名部分，隐藏完整路径
    path = Path(file)
    return f".../{path.name}"



