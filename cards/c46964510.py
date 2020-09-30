# 首席隐私执行官
from core.game import TimePoint
from utils.constants import EEffectDesc, ECardType, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin, EffUntil


class E4(EffTriggerCostMixin):
    """
    不能被攻击。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.FORBIDDEN,
                         host=c, trigger=True, force=True, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TRY_ATTACK:
            p = self.game.get_player(self.host)
            for c in p.on_field:
                if c is not None and c.type == ECardType.EMPLOYEE and c is not self.host:
                    return False
            return tp.args[1] is self.host
        return False

    def execute(self):
        self.reacted.pop().args[-1] = 0


class E3(EffTriggerCostMixin):
    """
    保护策略。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.PROTECT, host=host, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYING:
            f = ELocation.ON_FIELD + 2 - self.game.get_player(self.host).sp
            return (tp.args[1].location == f) & \
                   (tp.args[1].type == ECardType.STRATEGY) & \
                   (tp.args[1].cover == 1) & (self.host.location == f)
        return False

    def execute(self):
        tp = self.reacted.pop()
        self.game.invalid_tp(tp, tp.args[1], self)


class E2(EffTriggerCostMixin):
    """
    不能发动。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.FORBIDDEN, host=host, trigger=True, force=True,
                         passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TRY_ACTIVATE_STRATEGY:
            return tp.args[0] is self.host
        return False

    def execute(self):
        # TRY时点发动的效果不会被无效。
        self.reacted.pop().args[-1] = 0


class E1(EffTriggerCostMixin):
    """
    入场：盖放1策略。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SET_CARD, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if tp.args[0] is self.host:
                p = self.game.get_player(self.host)
                for pos in range(3, 6):
                    if p.on_field[pos] is None:
                        for c in p.hand:
                            if c.type == ECardType.STRATEGY:
                                tp = TimePoint(ETimePoint.TRY_SET_STRATEGY, self, [c, 1])
                                self.game.enter_time_point(tp)
                                if tp.args[-1]:
                                    return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return (c.location == ELocation.HAND + 2 - p.sp) & (c.type == ECardType.STRATEGY)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
        if tgt is not None:
            self.game.set_strategy(p, p, tgt, self)
            e2 = E2(tgt)
            tgt.register_effect(e2)
            tgt.register_effect(EffUntil(tgt, e2, lambda tp: tp.tp == ETimePoint.TURN_END))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E3(c))
    c.register_effect(E4(c))
