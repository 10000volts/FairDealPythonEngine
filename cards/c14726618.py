# 流量明星
from utils.constants import EEffectDesc, ECardType, ETimePoint
from utils.common_effects import EffCommonSummon, EffAttackLimit, EffUntil, EffTurnEndMixin


class E2(EffTurnEndMixin):
    """
    回合结束时回复攻击力。
    """
    def __init__(self, host, c, op, v):
        super().__init__(desc=EEffectDesc.EFFECT_END,
                         host=host, trigger=True, force=True, scr_arg=[c, op, v], no_reset=True, passive=True)

    def execute(self):
        self.scr_arg[0].remove_buff(self.scr_arg[1], self.scr_arg[2])
        self.host.remove_effect(self)


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
        p = self.game.get_player(self.host)
        for c in p.on_field:
            if c is not None and c.type == ECardType.EMPLOYEE:
                op, v = c.ATK.plus(2, False, self)
                c.register_effect(E2(self.host, c, op, v))
                e3 = EffAttackLimit(c, False)
                c.register_effect(e3)
                c.register_effect(EffUntil(c, e3, lambda tp: tp.tp == ETimePoint.TURN_END))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
