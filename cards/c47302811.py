# 大敌 库伦维尔
from utils.common_effects import EffPierce


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(EffPierce(c, 5000))
