# 沉稳
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType
from utils.common_effects import EffTriggerCostMixin, EffCommonStrategy


class E3(EffTriggerCostMixin):
    """
    更新攻击力。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) &\
                    (tp.args[0].location == self.host.location) & \
                    (len(tp.args[0].effects) == 0):
                return True
        return False

    def execute(self):
        self.reacted.pop().args[0].ATK.gain(600 if self.host.ATK.value > 600 else self.host.ATK.value, False, self)


class E1(EffCommonStrategy):
    """
    攻击力上升。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=c, can_invalid=False)

    def execute(self):
        pass


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E3(c))
