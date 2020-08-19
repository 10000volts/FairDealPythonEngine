# 保护
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType
from core.game import TimePoint
from utils.common_effects import EffTriggerCostMixin, EffAttackLimit, EffUntil


class E2(EffTriggerCostMixin):
    """
    不能被攻击。
    """
    def __init__(self, c, scr_arg):
        super().__init__(desc=EEffectDesc.PROTECT,
                         host=c, trigger=True, force=True, scr_arg=scr_arg, no_reset=True, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TRY_ATTACK:
            if (tp.args[1] is self.scr_arg) & (tp not in self.reacted):
                return True
        return False

    def execute(self):
        self.reacted.pop().args[-1] = 0


class E1(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.PROTECT, host=host)

    def condition(self, tp):
        if tp is None:
            for p in self.game.players:
                for c in p.on_field:
                    if c is not None and c.type == ECardType.EMPLOYEE and c.posture > 0:
                        tp = TimePoint(ETimePoint.TRY_CHOOSE_TARGET, self, [c, 1])
                        self.game.enter_time_point(tp)
                        if tp.args[-1]:
                            return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, lambda c: (((c.location & ELocation.ON_FIELD) > 0) &
                                                      (c.type == ECardType.EMPLOYEE) & (c.posture > 0)), self,
                                      True)
        if tgt is not None:
            e2 = E2(self.host, tgt)
            self.host.register_effect(e2, True)
            self.host.register_effect(EffUntil(self.host, e2,
                                      lambda tp: ((tp.tp == ETimePoint.TURN_BEGIN) &
                                                  (self.game.turn_player is self.game.get_player(self.host)))))
            tgt.register_effect(EffAttackLimit(tgt, False))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
