# 被窃取的机密
from utils.common_effects import EffCounterStgE2Mixin, EffCounterStgE1Mixin, EffTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc, ECardType


class E1(EffCounterStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host, scr_arg=[None], passive=True)

    def execute(self):
        pass


class E2(EffCounterStgE2Mixin):
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host, scr_arg=[ef], trigger=True)

    def condition(self, tp):
        return False


class E3(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.FORBIDDEN, host=host, trigger=True, force=True,
                         passive=True, can_invalid=False)

    def condition(self, tp):
        if tp.tp == ETimePoint.TRY_DISCARD:
            return (tp.args[0] is self.host) & (not tp.args[1])
        return False

    def execute(self):
        self.reacted.pop().args[-1] = 0


class E4(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.IN_GRAVE_END:
            return tp.args[0] is self.host
        return False

    def execute(self):
        op = self.game.players[self.game.get_player(self.host).sp]
        for c in op.on_field:
            if c is not None and c.type == ECardType.EMPLOYEE:
                c.ATK.gain(-self.host.ATK.value)
        self.game.deal_damage(self.host, op.leader, self.host.ATK.value)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e1 = E1(c)
    c.register_effect(e1)
    c.register_effect(E2(c, e1))
    c.register_effect(E3(c))
    c.register_effect(E4(c))
