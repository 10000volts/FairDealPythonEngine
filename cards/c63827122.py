# 婴儿
from utils.common_effects import EffLazyTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc, EGamePhase


class E2(EffLazyTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.ADDV_CHANGE, trigger=True,
                         force=True, passive=True, act_phase=EGamePhase.PUT_CARD)

    def condition(self, tp):
        if tp.tp == ETimePoint.SRC_ATK_CALCING:
            return (tp.args[0] is self.host) & (tp not in self.reacted)
        return False

    def execute(self):
        self.reacted.pop().args[1] = 0


class E1(EffLazyTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.ADDV_CHANGE, trigger=True,
                         force=True, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SRC_ATK_CALCING:
            return (tp.args[0] is self.host) & (tp not in self.reacted)
        return False

    def execute(self):
        self.reacted.pop().args[1] = 0


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
