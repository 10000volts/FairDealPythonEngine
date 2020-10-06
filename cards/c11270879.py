# 紧急致电
from utils.common_effects import EffCounterStgE2Mixin, EffCounterStgE1Mixin, EffTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc, ELocation, ECardType, EStrategyType
from core.game import TimePoint


class E3(EffTriggerCostMixin):
    def __init__(self, host, tp):
        super().__init__(desc=EEffectDesc.ACTIVATE_STRATEGY, host=host,
                         passive=True, trigger=True, force=True, no_reset=True, scr_arg=tp)

    def condition(self, tp):
        if tp.tp == ETimePoint.OUT_FIELD_END:
            return self.host is tp.args[0]
        return False

    def execute(self):
        def check(c):
            if (c.location == ELocation.HAND + 2 - p.sp) & (c.type == ECardType.STRATEGY):
                c.ATK.value += self.host.ATK.value
                if ((c.subtype & EStrategyType.COUNTER) > 0) & (c.cid != '11270879'):
                    f = c.effects[1].condition(TimePoint(ETimePoint.REDIRECT_COUNTER, self,
                                                         [self.scr_arg]))
                else:
                    f = c.effects[0].condition(None)
                c.ATK.value -= self.host.ATK.value
                return f
            return False
        for pos in range(3, 6):
            p = self.game.get_player(self.host)
            if p.on_field[pos] is None:
                tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
                if tgt is not None:
                    tgt.ATK.gain(self.host.ATK.value, False, self)
                    self.game.activate_strategy(p, p, tgt)
                self.host.remove_effect(self.host)
                break


class E1(EffCounterStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ACTIVATE_STRATEGY, host=host, scr_arg=[None], passive=True)

    def execute(self):
        self.host.register_effect(E3(self.host, self.scr_arg[0]))


class E2(EffCounterStgE2Mixin):
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.ACTIVATE_STRATEGY, host=host, scr_arg=[ef], trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.REDIRECT_COUNTER:
            tp = tp.args[0]
        else:
            if (self.host.turns == 0) | ((self.host.location & ELocation.ON_FIELD) == 0) | (self.host.cover == 0):
                return False
        if tp.tp == ETimePoint.PAID_COST:
            p = self.game.get_player(self.host)
            if ((tp.args[0].location & (2 - self.game.players[p.sp].sp)) > 0) & \
                    (tp.args[0].type == ECardType.STRATEGY):
                for c in p.hand:
                    if c.type == ECardType.STRATEGY:
                        c.ATK.value += self.host.ATK.value
                        if ((c.subtype & EStrategyType.COUNTER) > 0) & (c.cid != '11270879'):
                            if c.effects[1].condition(TimePoint(ETimePoint.REDIRECT_COUNTER, self,
                                                                [tp])):
                                c.ATK.value -= self.host.ATK.value
                                return True
                        else:
                            if c.effects[0].condition(None):
                                c.ATK.value -= self.host.ATK.value
                                return True
                        c.ATK.value -= self.host.ATK.value
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
