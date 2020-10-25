# 怨念的工作者
from utils.common_effects import EffTriggerCostMixin
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType


class E1(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DISCARD, host=host, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.IN_HAND_END:
            return (tp.args[0] is self.host) & ((tp.args[2] & ELocation.DECK) > 0)
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        self.game.discard(p, p, self.host, self)


class E2(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=host, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.IN_GRAVE_END:
            return tp.args[0] is self.host
        return False

    def execute(self):
        op = self.game.players[self.game.get_player(self.host).sp]
        for c in op.on_field:
            if c is not None and c.type == ECardType.EMPLOYEE:
                c.ATK.gain(-self.host.ATK.value)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
