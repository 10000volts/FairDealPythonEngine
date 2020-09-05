# 工作狂人
from utils.common_effects import EffLazyTriggerCostMixin, EffPierce
from utils.constants import EEffectDesc, ETimePoint, ELocation
from core.game import TimePoint


class E4(EffLazyTriggerCostMixin):
    """
    回手。
    """
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.SEND2HAND, trigger=True, force=True, no_reset=True)

    def condition(self, tp):
        return tp.tp == ETimePoint.TURN_END

    def execute(self):
        p = self.game.get_player(self.host)
        self.game.send2hand(p, p, self.host, self)


class E2(EffLazyTriggerCostMixin):
    """
    特招。
    """
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.SPECIAL_SUMMON, trigger=True, force=True,
                         no_reset=True)

    def condition(self, tp):
        return (tp.tp == ETimePoint.TURN_BEGIN) & (self.game.turn_player is self.game.get_player(self.host))

    def execute(self):
        if (self.host.location & ELocation.ON_FIELD) == 0:
            p = self.game.get_player(self.host)
            f = True
            for pos in range(0, 3):
                if f:
                    for posture in range(0, 2):
                        if p.on_field[pos] is None:
                            tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, p, pos, posture, 1])
                            self.game.enter_time_point(tp)
                            # 入场被允许
                            if tp.args[-1]:
                                self.game.special_summon(p, p, self.host, self)
                                f = False
                                break
                else:
                    break
        self.host.register_effect(EffPierce(self.host), True)
        self.host.register_effect(E4(self.host), True)
        self.host.remove_effect(self)


class E1(EffLazyTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.SPECIAL_SUMMON, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DISCARDED:
            return tp.args[0] is self.host
        return False

    def execute(self):
        self.host.register_effect(E2(self.host))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
