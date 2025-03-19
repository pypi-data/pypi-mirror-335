
def check_no_duplicates_2d(lst_2d):
    """检查二维列表的每一行是否无重复"""
    for row in lst_2d:
        # 将行转为集合，比较长度
        if len(row) != len(set(row)):
            return False
    return True

