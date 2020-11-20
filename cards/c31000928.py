# 法医博士
from importlib import import_module

from utils.constants import ETimePoint, EEffectDesc, ELocation, ECardType, EStrategyType, EChoice
from models.effect import Effect
from utils.common_effects import EffTriggerCostMixin


class E2(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.REGISTER_EFFECT, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            return (tp.args[0] is self.host) & (tp.sender is None) & \
                   (self.game.get_player(tp.args[1]) is not self.game.get_player(self.host)) & \
                   (tp.args[1].cid is not None)
        return False

    def execute(self):
        p = self.game.get_player(self.host)

        def check(c):
            return (c.location == ELocation.HAND + 2 - p.sp) & (c.type == ECardType.EMPLOYEE)
        c = self.reacted.pop().args[1]
        tgt = self.game.choose_target_from_func(p, p, check, self)
        if tgt is not None:
            try:
                m = import_module('cards.c{}'.format(c.cid))
                m.give(tgt)
            except Exception as ex:
                pass


class E1(Effect):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.REGISTER_EFFECT)

    def condition(self, tp):
        if tp.tp == ETimePoint.ASK4EFFECT:
            if (self.host.location & ELocation.ON_FIELD) > 0:
                p = self.game.get_player(self.host)
                for c in p.grave:
                    if c.type == ECardType.EMPLOYEE:
                        return True
        return False

    def cost(self, tp):
        p = self.game.get_player(self.host)

        def check(c):
            return (c.location == ELocation.GRAVE + 2 - p.sp) & (c.type == ECardType.EMPLOYEE)
        c = self.game.req4exile(check, self.game.get_player(self.host), 1, self)
        if c is not None and c.cid is not None:
            self.scr_arg = c.cid
            return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)

        def check(c):
            return (c.location == ELocation.ON_FIELD + 1 + p.sp) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, check, self)
        if tgt is not None:
            try:
                m = import_module('cards.c{}'.format(self.scr_arg))
                m.give(tgt)
            except Exception as ex:
                pass


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
