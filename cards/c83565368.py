# 网络暴民
from core.game import TimePoint
from utils.constants import EEffectDesc, ETimePoint, ELocation, EStrategyType
from utils.common_effects import EffTriggerCostMixin


class E2(EffTriggerCostMixin):
    """
    摧毁自己场上的卡。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            if tp.args[1] is self.host:
                p = self.game.get_player(self.host)
                for c in p.on_field:
                    if c is not None:
                        return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, lambda c: c in p.on_field, self, True)
        self.game.destroy(self.host, tgt, self)


class E1(EffTriggerCostMixin):
    """
    入场。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=c, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_ACTIVATE_STRATEGY:
            sd = self.game.get_player(self.host)
            if ((self.host.location & ELocation.HAND) > 0) &\
                    ((tp.args[0].subtype & EStrategyType.COUNTER) > 0) & \
                    ((tp.args[0].location & (2 - sd.sp)) > 0):
                for posture in range(0, 2):
                    for pos in range(0, 3):
                        if sd.on_field[pos] is None:
                            tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, sd, pos, posture, 1])
                            self.game.enter_time_point(tp)
                            # 入场被允许
                            return tp.args[-1]
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        self.game.special_summon(p, p, self.host, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
