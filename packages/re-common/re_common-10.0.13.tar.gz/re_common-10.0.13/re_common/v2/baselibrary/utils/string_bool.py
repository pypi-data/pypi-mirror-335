import re


def is_all_english_chars(s):
    return bool(re.match(r'^[A-Za-z]+$', s))


def contains_chinese_chars(s):
    return bool(re.search(r'[\u3400-\u9fff]', s))


def is_empty(value):
    """
    判断一个值是否为空。

    支持的类型：
    - None
    - 空字符串（去除空白后）
    - pandas 的 NaN
    - 其他可迭代类型（如列表、字典等）的长度为 0
    - 其他情况返回 False
    """
    # 如果是 None，直接返回 True
    if value is None:
        return True

    # 尝试处理 pandas 的 NaN
    try:
        import pandas as pd
        if pd.isna(value):
            return True
    except ImportError:
        pass  # 如果没有安装 pandas，跳过

    # 如果是字符串，检查去除空白后是否为空
    if isinstance(value, str):
        return value.strip() == ""

    # 处理其他可迭代类型（如列表、字典等）
    if hasattr(value, "__len__"):
        return len(value) == 0

    # 默认情况下，非 None、非空类型返回 False
    return False


class InvalidCharLengthError(Exception):
    """自定义异常类，用于处理输入字符长度不为 1 的情况"""
    pass


def is_single_cjk_char(char):
    """
    判断单个字符是否为中日韩字符
    :param char: 要判断的单个字符
    :return: 如果是中日韩字符返回 True，否则返回 False
    """
    # 检查输入字符的长度
    if len(char) != 1:
        raise InvalidCharLengthError("输入的字符串长度必须为 1，请提供单个字符进行判断。")
    code_point = ord(char)
    # 中日韩统一表意文字
    ranges = [
        (0x4E00, 0x9FFF),  # CJK 统一表意符号
        (0x3400, 0x4DBF),  # CJK 统一表意符号扩展 A
        (0x20000, 0x2A6DF),  # CJK 统一表意符号扩展 B
        (0x2A700, 0x2B73F),  # CJK 统一表意符号扩展 C
        (0x2B740, 0x2B81F),  # CJK 统一表意符号扩展 D
        (0x2B820, 0x2CEAF),  # CJK 统一表意符号扩展 E
        (0x2CEB0, 0x2EBEF),  # CJK 统一表意符号扩展 F
        (0x30000, 0x3134F),  # CJK 统一表意符号扩展 G
        (0x31350, 0x323AF),  # CJK 统一表意符号扩展 H
        (0x3300, 0x33FF),  # CJK 兼容符号
        (0xFE30, 0xFE4F),  # CJK 兼容形式
        (0xF900, 0xFAFF),  # CJK 兼容表意符号
        (0x2F800, 0x2FA1F),  # CJK 兼容表意符号补充
        (0x3105, 0x3129),  # 注音字母
        (0x31A0, 0x31BF),  # 注音字母扩展
        (0x3040, 0x309F),  # 平假名
        (0x30A0, 0x30FF),  # 片假名
        (0x31F0, 0x31FF),  # 片假名扩展
        (0xAC00, 0xD7AF),  # 韩文音节
        (0x1100, 0x11FF),  # 韩文字母
        (0xA960, 0xA97F),  # 韩文字母扩展 A
        (0xD7B0, 0xD7FF),  # 韩文字母扩展 B
    ]
    for start, end in ranges:
        if start <= code_point <= end:
            return True
    return False
