def bit_check(state, bit):
    """
    检测给定的状态中是否包含指定的位。
    :param state:
    :param bit:
    :return:
    """
    return state & bit != 0
