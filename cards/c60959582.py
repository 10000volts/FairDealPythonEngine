# 倔强格斗家 阿米娜
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType, ECardRank
from utils.common_effects import EffTriggerCostMixin


class E1(EffTriggerCostMixin):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.INVALID, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYING:
            if (tp.args[1] is self.host) & (tp.args[0].type == ECardType.EMPLOYEE) & \
                    (tp.args[0].rank == ECardRank.TRUMP):
                return True
        return False

    def execute(self):
        self.game.invalid_tp(self.reacted.pop(), self.host, self)


class E2(EffTriggerCostMixin):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.ATTACKED:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (tp.args[0] is self.host) & \
                   (tp.args[1].rank == ECardRank.TRUMP):
                return True
        return False

    def execute(self):
        self.host.ATK.gain(500, False, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))