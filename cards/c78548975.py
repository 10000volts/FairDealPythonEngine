# 诈骗师
from utils.common_effects import EffPierce, EffTriggerCostMixin, EffUntil
from utils.constants import EEffectDesc, ETimePoint, ECardType, ELocation, EEmployeeType
from core.game import TimePoint


class E4(EffTriggerCostMixin):
    def __init__(self, host, op1, v1, op2, v2):
        super().__init__(host=host, desc=EEffectDesc.ATK_CHANGE, trigger=True, force=True,
                         scr_arg=[op1, v1, op2, v2], no_reset=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.ATTACK_COMPLETE:
            return ((tp.args[0] is self.host) & (tp.args[1].subtype != EEmployeeType.LEADER)) | \
                   (tp.args[1] is self.host)
        return False

    def execute(self):
        tp = self.reacted.pop()
        if tp.args[0].location & ELocation.ON_FIELD:
            tp.args[0].remove_buff(self.scr_arg[0], self.scr_arg[1])
        if tp.args[1].location & ELocation.ON_FIELD:
            tp.args[1].remove_buff(self.scr_arg[2], self.scr_arg[3])
        self.host.remove_effect(self)


class E3(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.ATK_CHANGE, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.ATTACKING:
            return ((tp.args[0] is self.host) & (tp.args[1].type == ECardType.EMPLOYEE)) | \
                   (tp.args[1] is self.host)
        return False

    def execute(self):
        tp = self.reacted.pop()
        t = tp.args[0].ATK.value
        op1, v1 = tp.args[0].ATK.become(tp.args[1].ATK.value, False, self)
        op2, v2 = tp.args[1].ATK.become(t, False, self)
        self.host.register_effect(E4(self.host, op1, v1, op2, v2))


class E2(EffTriggerCostMixin):
    """
    战伤一半回血。
    """
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.HEAL, trigger=True, force=True, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEALING_DAMAGE:
            if (tp.args[0] is self.host) & (tp.sender is None):
                tp = TimePoint(ETimePoint.TRY_HEAL, self,
                               [self.host, self.game.get_player(self.host).leader, int(tp.args[2] / 2), 1])
                return tp.args[-1]
        return False

    def execute(self):
        tp = self.reacted.pop()
        t = tp.args[2]
        tp.args[2] = int(tp.args[2] / 2)
        p = self.game.get_player(self.host)
        self.game.heal(self.host, p.leader, t - tp.args[2], self)


class E1(EffTriggerCostMixin):
    """
    攻击雇员时赋予效果: 战伤一半回血、攻击后移除效果。
    """
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.REGISTER_EFFECT, trigger=True, force=True,
                         passive=True, ef_id=EEffectDesc.PIERCE)

    def condition(self, tp):
        if tp.tp == ETimePoint.ATTACKING:
            return (tp.args[0] is self.host) & (tp.args[1].type == ECardType.EMPLOYEE)
        return False

    def execute(self):
        e2 = E2(self.host)
        self.host.register_effect(e2)
        self.host.register_effect(EffUntil(self.host, e2, lambda tp: (tp.tp == ETimePoint.ATTACKED and
                                                                      tp.args[0] is self.host)))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(EffPierce(c))
    c.register_effect(E1(c))
    c.register_effect(E3(c))
