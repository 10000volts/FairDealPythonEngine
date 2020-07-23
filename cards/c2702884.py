# 陷阱合同
from utils.common_effects import EffCounterStgE2Mixin, EffCounterStgE1Mixin, EffTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc, ELocation


class E1(EffCounterStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=host, scr_arg=[None])

    def execute(self):
        # 输出
        super().execute()
        # 攻击力下降
        self.scr_arg[0].args[0].ATK.gain(-self.host.ATK.value)


class E2(EffCounterStgE2Mixin, EffTriggerCostMixin):
    """
    我方玩家被攻击时
    """
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=host, scr_arg=[ef], trigger=True)

    def condition(self, tp):
        if self.host.turns:
            if tp.tp == ETimePoint.SUCC_SUMMON:
                return ((self.host.location & ELocation.ON_FIELD) > 0) &\
                       self.host.cover & (tp not in self.reacted)
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
