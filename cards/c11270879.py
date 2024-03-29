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
                c.ATK.value += v
                if ((c.subtype & EStrategyType.COUNTER) > 0) & (c.cid != '11270879'):
                    f = c.effects[1].condition(TimePoint(ETimePoint.REDIRECT_COUNTER, self,
                                                         [self.scr_arg]))
                else:
                    f = c.effects[0].condition(None)
                c.ATK.value -= v
                return f
            return False
        for pos in range(3, 6):
            p = self.game.get_player(self.host)
            if p.on_field[pos] is None:
                v = min(self.host.ATK.value, 1000)
                tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
                if tgt is not None:
                    tgt.ATK.gain(v, False, self)
                    if tgt.subtype & EStrategyType.COUNTER:
                        # 设置时点
                        tgt.effects[0].scr_arg[0] = self.scr_arg
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
            self.reacted.append(tp)
        else:
            if (self.host.turns == 0) | ((self.host.location & ELocation.ON_FIELD) == 0) | (self.host.cover == 0):
                return False
        if tp.tp == ETimePoint.ACTIVATING_STRATEGY:
            p = self.game.get_player(self.host)
            # todo: 取消不能响应反制牌限制
            if ((tp.args[0].location & (2 - self.game.players[p.sp].sp)) > 0) & ((tp.args[0].subtype & EStrategyType.COUNTER) == 0):
                for c in p.hand:
                    if c.type == ECardType.STRATEGY:
                        v = min(self.host.ATK.value, 1000)
                        c.ATK.value += v
                        if ((c.subtype & EStrategyType.COUNTER) > 0) & (c.cid != '11270879'):
                            if c.effects[1].condition(TimePoint(ETimePoint.REDIRECT_COUNTER, self,
                                                                [tp])):
                                c.ATK.value -= v
                                return super().condition(tp)
                        else:
                            if c.effects[0].condition(None):
                                c.ATK.value -= v
                                return super().condition(tp)
                        c.ATK.value -= v
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
