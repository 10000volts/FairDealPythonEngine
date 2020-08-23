# 皮亚娜
from utils.common_effects import EffLazyTriggerCostMixin
from utils.constants import EEffectDesc, EGamePhase, ETimePoint


class E1(EffLazyTriggerCostMixin):
    """
    加buff
    """
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.ADDV_CHANGE, trigger=True,
                         act_phase=EGamePhase.EXTRA_DATA)

    def condition(self, tp):
        return tp.tp == ETimePoint.PH_EXTRA_DATA_END and tp not in self.reacted

    def execute(self):
        self.host.ATK.change_adv(-10000)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
