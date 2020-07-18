# 龙骑士 盖亚Coser
from utils.common_effects import EffPierce


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(EffPierce(c))
