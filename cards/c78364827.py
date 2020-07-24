# 老虎机
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffCommonStrategy, EffTriggerCostMixin


class E1(EffCommonStrategy):
    """
    攻击力上升并自摧毁。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=c, passive=True)

    def execute(self):
        pass


class E2(EffTriggerCostMixin):
    """
    攻击力上升并自摧毁。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) &\
                    (tp not in self.reacted):
                return True
        return False

    def execute(self):
        self.game.count(self.host, 'SLOT')
        if self.host.sign['SLOT'] == 5:
            self.game.destroy(self.host, self.host, self)
            c = self.reacted.pop().args[0]
            if c.location & ELocation.ON_FIELD:
                c.ATK.gain(self.host.ATK.value)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
