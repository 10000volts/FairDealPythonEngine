# 监守自盗的雷西
from core.game import TimePoint
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin

from random import randint


class E1(EffTriggerCostMixin):
    """
    随机丢弃手牌。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DISCARD, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_END:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (tp not in self.reacted):
                for c in self.game.get_player(self.host).hand:
                    tp = TimePoint(ETimePoint.TRY_DISCARD, self, [c, 1])
                    self.game.enter_time_point(tp)
                    if tp.args[-1]:
                        return True
        return False

    def execute(self):
        # 输出
        super().execute()

        p = self.game.get_player(self.host)
        # todo: 不会出现不能被丢弃的卡。
        if len(p.hand):
            i = randint(0, len(p.hand) - 1)
            self.game.discard(p, p, p.hand[i], self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
