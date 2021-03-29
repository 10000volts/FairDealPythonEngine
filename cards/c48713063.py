# 勇敢的记者
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffLazyTriggerCostMixin, EffNextTurnMixin, EffUntil
from core.game import TimePoint, Effect


class E3(Effect):
    """
    可以从手牌直接入场。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=host, no_reset=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.ASK4EFFECT:
            if self.host.location & ELocation.HAND:
                sd = self.game.get_player(self.host)
                for posture in range(0, 2):
                    for pos in range(0, 3):
                        if sd.on_field[pos] is None:
                            tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, sd, pos, posture, 1])
                            self.game.enter_time_point(tp)
                            # 入场被允许
                            return tp.args[-1]
        return False

    def execute(self):
        # 从手牌入场
        p = self.game.get_player(self.host)
        self.game.special_summon(p, p, self.host, self)


class E2(EffNextTurnMixin):
    """
    赋予效果。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=host, trigger=True, force=True,
                         no_reset=True, passive=True)

    def execute(self):
        e3 = E3(self.host)
        self.host.register_effect(e3)
        self.host.register_effect(EffUntil(self.host, e3, lambda tp: tp.tp == ETimePoint.TURN_END))
        self.host.remove_effect(self)


class E1(EffLazyTriggerCostMixin):
    """
    下次我方回合开始时获得效果。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.REGISTER_EFFECT, host=host, trigger=True, force=True,
                         no_reset=True, passive=True)

    def condition(self, tp):
        return (tp.tp == ETimePoint.BLOCKED) & (self.game.op_player is self.game.get_player(tp.args[1]))

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 注册效果
        self.host.register_effect(E2(self.host))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
