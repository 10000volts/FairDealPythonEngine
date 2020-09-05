# 终结时刻
from utils.constants import EEffectDesc, ETimePoint
from utils.common_effects import EffTriggerCostMixin, EffCommonStrategy, EffUntil


class E2(EffTriggerCostMixin):
    """
    对方不能回复生命
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.FORBIDDEN, host=c, trigger=True, force=True,
                         no_reset=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if (tp.tp == ETimePoint.TRY_HEAL) | (tp.tp == ETimePoint.HEALING):
            if (tp.args[1] is self.game.players[self.game.get_player(self.host).sp].leader):
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        self.reacted.pop().args[-1] = 0


class E1(EffCommonStrategy):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.REGISTER_EFFECT, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        e2 = E2(self.host)
        p = self.game.get_player(self.host)
        self.host.register_effect(e2)
        self.host.register_effect(EffUntil(self.host, e2, lambda tp:
                                           (tp.tp == ETimePoint.TURN_BEGIN)
                                           & (self.game.turn_player is p)))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
