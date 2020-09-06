# 救火队长
from utils.common_effects import EffTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc
from core.game import TimePoint


class E2(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.ATK_GAIN, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            return tp.args[1] is self.host
        return False

    def execute(self):
        self.host.ATK.gain(1000, True, self)


class E1(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.SPECIAL_SUMMON, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.OUT_HAND_END:
            p = self.game.get_player(self.host)
            if len(p.hand) == 0:
                for pos in range(0, 3):
                    for posture in range(0, 2):
                        if p.on_field[pos] is None:
                            tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, p, pos, posture, 1])
                            self.game.enter_time_point(tp)
                            # 入场被允许
                            if tp.args[-1]:
                                return True
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
