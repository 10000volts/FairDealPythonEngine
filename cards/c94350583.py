# 堆笑推销员
from core.game import TimePoint, GameCard
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin, EffTaunt


class E1(EffTriggerCostMixin):
    """
    遗言。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.OUT_FIELD:
            if (tp.args[0] is self.host) & (tp not in self.reacted) & (self.host.ATK.value > 1000):
                p = self.game.get_player(self.host)
                for posture in range(0, 2):
                    for pos in range(0, 3):
                        tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, p, pos, posture, 1])
                        self.game.enter_time_point(tp)
                        if tp.args[-1]:
                            return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        c = GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), self.host.cid, True)
        c.ATK.become(int(self.host.ATK.value / 2))
        self.game.special_summon(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(EffTaunt(c))
    c.register_effect(E1(c))
