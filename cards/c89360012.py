# 识破
from utils.common_effects import EffCounterStgE2Mixin, EffCounterStgE1Mixin, EffTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc, ELocation, ECardType


class E1(EffCounterStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.INVALID, host=host, scr_arg=[None], passive=True)

    def execute(self):
        # 无效。
        self.scr_arg[0].args[-1] = 0


class E2(EffCounterStgE2Mixin, EffTriggerCostMixin):
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.INVALID, host=host, scr_arg=[ef], trigger=True)

    def condition(self, tp):
        if (self.host.turns > 0) & (tp.tp == ETimePoint.PAID_COST):
            if self.host.location & ELocation.ON_FIELD:
                if self.host.cover:
                    if (tp.args[0].ATK.value <= self.host.ATK.value) & (tp not in self.reacted) & \
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
