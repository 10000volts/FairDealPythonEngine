# 金钱教主
from utils.common_effects import EffTriggerCostMixin
from utils.constants import EEffectDesc, ETimePoint, ECardType, ECardRank, ELocation


class E2(EffTriggerCostMixin):
    """
    回合结束时回复攻击力。
    """
    def __init__(self, host, op, v):
        super().__init__(desc=EEffectDesc.EFFECT_END,
                         host=host, trigger=True, force=True, scr_arg=[op, v], no_reset=True, passive=True)

    def condition(self, tp):
        return (tp.tp == ETimePoint.TURN_END) & (self.game.turn_player is self.game.get_player(self.host))

    def execute(self):
        self.host.remove_buff(self.scr_arg[0], self.scr_arg[1])
        self.host.remove_effect(self)


class E1(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.INVALID, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.PAID_COST:
            p = self.game.get_player(self.host)
            if ((tp.args[0].location & (1 + p.sp)) > 0) & (tp.args[0].type != ECardType.LEADER) & \
                    (not tp.sender.passive) & (not tp.sender.no_reset) & tp.sender.can_invalid & \
                    ((self.host.location & ELocation.ON_FIELD) > 0):
                for c in p.hand:
                    if (c.rank == ECardRank.TRUMP) & (c.ATK.value > 0):
                        return True
        if tp.tp == ETimePoint.DESTROYING:
            p = self.game.get_player(self.host)
            if tp.args[1] is self.host:
                for c in p.hand:
                    if (c.rank == ECardRank.TRUMP) & (c.ATK.value > 0):
                        return True
        return False

    def cost(self, tp):
        def check(c):
            return (c.location == ELocation.HAND + 2 - p.sp) & (c.rank == ECardRank.TRUMP) & (c.ATK.value > 0)

        self.reacted.append(tp)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
        if tgt is not None:
            tgt.ATK.become(0, False, self)
            return True
        return False

    def execute(self):
        tp = self.reacted.pop()
        self.game.invalid_tp(tp, tp.args[1], self)
        op, v = self.host.ATK.gain(1000, False, self)
        self.host.register_effect(E2(self.host, op, v))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
