# 高级智库
from core.game import TimePoint
from utils.constants import EEffectDesc, ECardType, ETimePoint, EStrategyType, ELocation
from utils.common_effects import EffTriggerCostMixin


class E3(EffTriggerCostMixin):
    """
    抗性
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.INVALID, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.INFLUENCING:
            p = self.game.get_player(self.host)
            return (tp.args[0] is self.host) & ((self.host.location & ELocation.ON_FIELD) > 0) & \
                   (tp.sender.host.type == ECardType.STRATEGY) & ((tp.sender.host.location & (1 + p.sp)) > 0)
        return False

    def execute(self):
        self.reacted.pop().args[-1] = 0


class E2(EffTriggerCostMixin):
    """
    EFF*2
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.PROPERTY_CHANGE, host=c, trigger=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.SET_STRATEGY:
            return (tp.args[0].location & (2 - self.game.get_player(self.host).sp) > 0) & \
                   ((self.host.location & ELocation.ON_FIELD) > 0)
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        tp = self.reacted.pop()
        tp.args[0].ATK.plus(2, False, self)


class E1(EffTriggerCostMixin):
    """
    入场：盖放1反制策略。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SET_CARD, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if tp.args[0] is self.host:
                p = self.game.get_player(self.host)
                for pos in range(3, 6):
                    if p.on_field[pos] is None:
                        for c in p.grave:
                            if (c.type == ECardType.STRATEGY) & ((c.subtype & EStrategyType.COUNTER) > 0):
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
            return (c.location == ELocation.HAND + 2 - p.sp) & (c.type == ECardType.STRATEGY) & \
                   ((c.subtype & EStrategyType.COUNTER) > 0)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
        if tgt is not None:
            self.game.set_strategy(p, p, tgt, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
    c.register_effect(E3(c))
