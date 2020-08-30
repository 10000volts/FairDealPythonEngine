# 街头混混
from utils.common_effects import EffAgile


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(EffAgile(c))
