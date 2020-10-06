# 默认领袖
from utils.common_effects import EffProtectProtocol, EffHPLimit


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(EffHPLimit(c))
    # 保护协议
    c.register_effect(EffProtectProtocol(c))
