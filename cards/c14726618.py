# 流量明星
from utils.constants import EEffectDesc, ECardType, ELocation
from utils.common_effects import EffCommonSummon


class E1(EffCommonSummon):
    """
    我方场上全部雇员ATK翻倍。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)
        for em in p.on_field:
            if em is not None and em.type == ECardType.EMPLOYEE:
                em.ATK.plus(2)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
