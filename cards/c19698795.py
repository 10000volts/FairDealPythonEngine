# 尽职的安保人员
from utils.common_effects import EffTaunt


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(EffTaunt(c))
