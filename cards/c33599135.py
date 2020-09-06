# 盘活
from utils.common_effects import EffCounterStgE2Mixin, EffCounterStgE1Mixin, EffTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc, ELocation
from core.game import TimePoint


class E1(EffCounterStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.INVALID, host=host, scr_arg=[None], passive=True)

    def execute(self):
        # 无效攻击。
        self.game.invalid_tp(self.scr_arg[0], self.scr_arg[0].args[0], self)
        # 生命力回复
        c = self.game.get_player(self.host).leader
        v = self.scr_arg[0].args[0].ATK.value
        tp = TimePoint(ETimePoint.TRY_HEAL, self, [self.host, c, v, 1])
        self.game.enter_time_point(tp)
        if tp.args[-1]:
            self.game.heal(self.host, c, v, self)


class E2(EffCounterStgE2Mixin, EffTriggerCostMixin):
    """
    我方玩家被攻击时
    """
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.INVALID, host=host, scr_arg=[ef], trigger=True)

    def condition(self, tp):
        if self.host.turns:
            if tp.tp == ETimePoint.ATTACKING:
                if self.host.location & ELocation.ON_FIELD:
                    p = self.game.get_player(self.host)
                    if self.host.cover:
                        return tp.args[1] is p.leader
        return False


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e1 = E1(c)
    c.register_effect(e1)
    c.register_effect(E2(c, e1))
