# 精致利己主义者
from random import randint

from utils.common_effects import EffCommonSummon
from utils.constants import EEffectDesc, ECardType, ETimePoint
from core.game import TimePoint


class E1(EffCommonSummon):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.DISCARD, force=True)

    def execute(self):
        cl = list()
        p = self.game.get_player(self.host)
        for c in p.hand:
            if c.type == ECardType.EMPLOYEE:
                tp = TimePoint(ETimePoint.TRY_DISCARD, self, [c, 1])
                self.game.enter_time_point(tp)
                if tp.args[-1]:
                    cl.append(c)
        if len(cl) > 1:
            for i in range(0, 2):
                ind = randint(0, len(cl) - 1)
                self.game.discard(p, p, cl[ind], self)
                cl.pop(ind)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
