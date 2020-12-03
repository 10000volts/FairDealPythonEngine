# 瓦解
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin, EffCommonStrategy, EGamePhase


class E3(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.ADDV_CHANGE, trigger=True,
                         force=True, passive=True, act_phase=EGamePhase.PUT_CARD)

    def condition(self, tp):
        if tp.tp == ETimePoint.SRC_ATK_CALCING:
            return tp.args[0] is self.host
        return False

    def execute(self):
        self.reacted.pop().args[1] /= 5


class E4(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.ADDV_CHANGE, trigger=True,
                         force=True, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SRC_ATK_CALCING:
            return tp.args[0] is self.host
        return False

    def execute(self):
        self.reacted.pop().args[1] /= 5


class E1(EffCommonStrategy):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DAMAGE_CHANGE, host=c, passive=True)

    def execute(self):
        pass


class E2(EffTriggerCostMixin):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DAMAGE_CHANGE, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEALING_DAMAGE:
            op = self.game.players[self.game.get_player(self.host).sp]
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover)\
                    & ((tp.args[0].location & (2 - op.sp)) > 0) & (tp.args[1] is op.leader):
                return True
        return False

    def execute(self):
        self.reacted.pop().args[2] += min(self.host.ATK.value, 800)


def give(c):
    """
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
    c.register_effect(E3(c))
    c.register_effect(E4(c))
