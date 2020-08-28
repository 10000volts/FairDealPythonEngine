# 伺机待发
from utils.constants import EEffectDesc, ETimePoint
from utils.common_effects import EffTriggerCostMixin, EffCommonStrategy


class E4(EffTriggerCostMixin):
    """
    EFF+EFF
    """
    def __init__(self, c, e2):
        super().__init__(desc=EEffectDesc.PROPERTY_CHANGE, host=c, trigger=True, force=True,
                         no_reset=True, scr_arg=e2)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.ACTIVATING_STRATEGY:
            if ((tp.args[0].location & (2 - self.game.get_player(self.host).sp)) > 0) & \
                    (tp not in self.reacted):
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        self.reacted.pop().ATK.gain(self.host.ATK.value)
        self.host.remove_effect(self.scr_arg)
        self.host.remove_effect(self)


class E3(EffTriggerCostMixin):
    """
    EFF-EFF（偷偷地）
    """
    def __init__(self, c, op, v):
        super().__init__(desc=EEffectDesc.PROPERTY_CHANGE, host=c, trigger=True, force=True,
                         no_reset=True, passive=True, scr_arg=[op, v])

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.TRIED_ACTIVATE_STRATEGY:
            if ((tp.args[0].location & (2 - self.game.get_player(self.host).sp)) > 0) & \
                    (tp not in self.reacted):
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        self.reacted.pop().args[0].ATK.remove(self.scr_arg[0], self.scr_arg[1])
        self.host.remove_effect(self)


class E2(EffTriggerCostMixin):
    """
    EFF+EFF
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.PROPERTY_CHANGE, host=c, trigger=True, force=True,
                         no_reset=True, passive=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.TRY_ACTIVATE_STRATEGY:
            if ((tp.args[0].location & (2 - self.game.get_player(self.host).sp)) > 0) & \
                    (tp not in self.reacted):
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        op, v = self.reacted.pop().ATK.gain(self.host.ATK.value)
        self.host.register_effect(E3(self.host, op, v))


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
        self.host.register_effect(e2)
        self.host.register_effect(E4(self.host, e2))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
