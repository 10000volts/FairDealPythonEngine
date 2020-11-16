# 金属乐迷
from random import randint

from utils.constants import EEffectDesc, ETimePoint, ECardType
from utils.common_effects import EffTriggerCostMixin


class E1(EffTriggerCostMixin):
    """
    击溃对方雇员时。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            return (tp.args[0] is self.host) & (tp.sender is None) & \
                   (self.game.get_player(tp.args[1]) is not self.game.get_player(self.host))
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        cs = list()
        for c in p.hand:
            if c.type == ECardType.EMPLOYEE:
                cs.append(c)
        cs[randint(0, len(cs) - 1)].ATK.gain(500, False, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
