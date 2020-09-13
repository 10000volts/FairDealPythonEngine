# 紧急致电
from utils.common_effects import EffCounterStgE2Mixin, EffCounterStgE1Mixin, EffTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc, ELocation, ECardType


class E3(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ACTIVATE_STRATEGY, host=host,
                         passive=True, trigger=True, force=True, no_reset=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.OUT_FIELD_END:
            return self.host is tp.args[0]
        return False

    def execute(self):
        def check(c):
            if (c.location == ELocation.HAND + 2 - p.sp) & (c.type == ECardType.STRATEGY):
                c.ATK.value += self.host.ATK.value
                f = c.effects[0].condition(None)
                c.ATK.value -= self.host.ATK.value
                return f
            return False
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self, True, False)
        if tgt is not None:
            tgt.ATK.gain(self.host.ATK.value, False, self)
            self.game.activate_strategy(p, p, tgt)
        self.host.remove_effect(self.host)


class E1(EffCounterStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ACTIVATE_STRATEGY, host=host, scr_arg=[None], passive=True)

    def execute(self):
        self.host.register_effect(E3(self.host))


class E2(EffCounterStgE2Mixin, EffTriggerCostMixin):
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.ACTIVATE_STRATEGY, host=host, scr_arg=[ef], trigger=True)

    def condition(self, tp):
        if self.host.turns:
            if tp.tp == ETimePoint.ACTIVATING_STRATEGY:
                p = self.game.get_player(self.host)
                if ((self.host.location & ELocation.ON_FIELD) > 0) &\
                   self.host.cover & \
                   ((tp.args[0].location & (2 - self.game.players[p.sp].sp)) > 0):
                    for c in p.hand:
                        if c.type == ECardType.STRATEGY and c.effects[0].condition(None):
                            return True
        return False


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e1 = E1(c)
    c.register_effect(e1)
    c.register_effect(E2(c, e1))
