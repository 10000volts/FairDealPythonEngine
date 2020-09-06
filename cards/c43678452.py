# 偶像新星
from utils.common_effects import EffPierce, EffLazyTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc


class E2(EffLazyTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.ATK_GAIN, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            return tp.args[0] is self.host
        return False

    def execute(self):
        self.host.ATK.gain(800, True, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(EffPierce(c))
    c.register_effect(E2(c))
