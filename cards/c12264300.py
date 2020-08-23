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
                    (tp not in self.reacted) & (tp.args[0].location == self.host.location) & \
                    (len(tp.args[0].effects) == 0):
                return True
        return False

    def execute(self):
        self.reacted.pop().args[0].ATK.update()


class E1(EffCommonStrategy):
    """
    攻击力上升。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=c)

    def execute(self):
        p = self.game.get_player(self.host)
        for c in p.on_field:
            if c is not None and c.type == ECardType.EMPLOYEE and len(c.effects) == 0:
                c.ATK.update()


class E2(EffTriggerCostMixin):
    """
    攻击力上升。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=c, trigger=True, force=True, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.ATK_CALCING:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) & (tp not in self.reacted)\
                    & (tp.args[0].type == ECardType.EMPLOYEE) & (tp.args[0].location == self.host.location) & \
                    (len(tp.args[0].effects) == 0):
                return True
        return False

    def execute(self):
        self.reacted.pop().args[1] += self.host.ATK.value if self.host.ATK.value < 600 else 600


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
    c.register_effect(E3(c))
