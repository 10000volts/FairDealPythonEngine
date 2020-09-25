# 社会学家
from utils.common_effects import EffTriggerCostMixin
from utils.constants import EEffectDesc, ETimePoint, ELocation


class E2(EffTriggerCostMixin):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.PROPERTY_CHANGE, host=c, trigger=True, force=True, passive=True)

    def condition(self, tp):
        if (tp.tp == ETimePoint.ATK_CALCING) | (tp.tp == ETimePoint.DEF_CALCING):
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (tp.args[0] is self.host):
                return True
        return False

    def execute(self):
        count = 0
        for p in self.game.players:
            for c in p.on_field:
                if c is not None:
                    count += 1
        self.reacted.pop().args[1] = count * 700


class E1(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.PROPERTY_CHANGE, host=host, trigger=True, force=True,
                         passive=True)

    def condition(self, tp):
        if (tp.tp == ETimePoint.IN_FIELD_END) | (tp.tp == ETimePoint.OUT_FIELD_END):
            if (self.host.location & ELocation.ON_FIELD) > 0:
                return True
        return tp.tp == ETimePoint.SUCC_SUMMON and tp.args[0] is self.host

    def execute(self):
        self.host.ATK.update()
        self.host.DEF.update()


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
