# 流量明星
from utils.constants import EEffectDesc, ECardType, ELocation, ETurnPhase
from utils.common_effects import EffCommonSummon, EffAttackLimit, EffUntil


class E1(EffCommonSummon):
    """
    ATK翻倍。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.PROPERTY_CHANGE, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self)
        if tgt is not None:
            tgt.ATK.plus(2, False, self)
            e2 = EffAttackLimit(tgt, False)
            tgt.register_effect(e2)
            tgt.register_effect(EffUntil(tgt, e2, lambda tp: tp.tp == ETurnPhase.ENDING))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
