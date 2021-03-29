# 数据商人
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffLazyTriggerCostMixin


class E1(EffLazyTriggerCostMixin):
    """
    攻击力上升。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) &\
                    (tp.args[0] is not self.host):
                return True
        return False

    def execute(self):
        self.host.ATK.gain(300, False, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
