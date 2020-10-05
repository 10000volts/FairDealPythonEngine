# 识破
from utils.common_effects import EffCounterStgE2Mixin, EffCounterStgE1Mixin, EffTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc, ELocation, ECardType


class E1(EffCounterStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.INVALID, host=host, scr_arg=[None], passive=True)

    def execute(self):
        # 无效。
        self.game.invalid_tp(self.scr_arg[0], self.scr_arg[0].args[0], self)


class E2(EffCounterStgE2Mixin, EffTriggerCostMixin):
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.INVALID, host=host, scr_arg=[ef], trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.REDIRECT_COUNTER:
            tp = tp.args[0]
        else:
            if (self.host.turns == 0) | ((self.host.location & ELocation.ON_FIELD) == 0) | (self.host.cover == 0):
                return False
        if tp.tp == ETimePoint.PAID_COST:
            if (tp.args[0].ATK.value <= self.host.ATK.value) & \
                    ((tp.args[0].location & (1 + self.game.get_player(self.host).sp)) > 0) & \
                    (tp.args[0].type == ECardType.STRATEGY):
                return True
        return False


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e1 = E1(c)
    c.register_effect(e1)
    c.register_effect(E2(c, e1))
