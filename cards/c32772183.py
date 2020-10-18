# 匆忙的上班族

from utils.common_effects import EffTurnCostMixin
from utils.constants import EEffectDesc, ETimePoint, ELocation
from core.game import TimePoint


class E1(EffTurnCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.IN_HAND_END:
            p = self.game.get_player(self.host)
            if (tp.args[0] is self.host) & ((tp.args[2] & ELocation.DECK) > 0) & \
                (self.ef_id not in p.ef_limiter):
                for pos in range(0, 3):
                    for posture in range(0, 2):
                        if p.on_field[pos] is None:
                            tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, p, pos, posture, 1])
                            self.game.enter_time_point(tp)
                            if tp.args[-1]:
                                return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        for pos in range(0, 3):
            for posture in range(0, 2):
                if p.on_field[pos] is None:
                    tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, p, pos, posture, 1])
                    self.game.enter_time_point(tp)
                    if tp.args[-1]:
                        self.game.special_summon(p, p, self.host, self)
                        return


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
