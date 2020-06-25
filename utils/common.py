def bit_check(state, bit):
    """
    检测给定的状态中是否包含指定的位。
    :param state:
    :param bit:
    :return:
    """
    return state & bit != 0


def adj_pos(x, y):
    """
    生成临近的合法坐标。
    :param x:
    :param y:
    :return:
    """
    p = y * 6 + x
    if p == 0:
        return p + 1, p + 6
    elif p < 6:
        return p - 1, p + 1, p + 6
    elif p < 30:
        return p - 6, p - 1, p + 1, p + 6
    elif p < 35:
        return p - 6, p - 1, p + 1
    else:
        return p - 6, p - 1
