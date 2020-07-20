# 经营有方
from core.game import TimePoint
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin, EffCommonStrategy


class E1(EffCommonStrategy):
    """
    回复生命。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.HEAL, host=c)

    def execute(self):
        pass


class E2(EffTriggerCostMixin):
    """
    回复生命。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.HEAL, host=c, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_ENDING:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) & (tp not in self.reacted):
                return True
        return False

    def execute(self):
        # 输出
        super().execute()

        p = self.game.get_player(self.host)
        tp = TimePoint(ETimePoint.TRY_HEAL, self, [self.host, p.leader, self.host.ATK.value, 1])
        self.game.enter_time_point(tp)
        if tp.args[-1]:
            self.game.heal(self.host, p.leader, self.host.ATK.value, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
