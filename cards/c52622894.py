# 报复
from utils.common_effects import EffCounterStgE2Mixin, EffCounterStgE1Mixin, EffTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc, ELocation, ECardType


class E1(EffCounterStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.INVALID, host=host, scr_arg=[None], passive=True)

    def execute(self):
        if self.scr_arg[0].args[0].location & ELocation.ON_FIELD:
            self.scr_arg[0].args[0].ATK.gain(-self.scr_arg[0].args[1].ATK.value, False,
                                             self)


class E2(EffCounterStgE2Mixin, EffTriggerCostMixin):
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=host, scr_arg=[ef], trigger=True)

    def condition(self, tp):
        if self.host.turns:
            if tp.tp == ETimePoint.DESTROYING:
                if self.host.location & ELocation.ON_FIELD:
                    p = self.game.get_player(self.host)
                    if self.host.cover:
                        if (tp.args[1].location == ELocation.ON_FIELD + 2 - p.sp) & \
                                (tp.args[1].type == ECardType.EMPLOYEE):
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
