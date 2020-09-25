# 连发左轮
from utils.common_effects import EffSingleStgE1Mixin, EffSingleStgE2, EffSingleStgE3Mixin,\
    EffTriggerCostMixin
from utils.constants import EEffectDesc, ELocation, ECardType, ETimePoint


class E4(EffTriggerCostMixin):
    def __init__(self, host, c):
        super().__init__(desc=EEffectDesc.EXTRA_CHANCE, host=host, trigger=True, force=True,
                         scr_arg=c)

    def condition(self, tp):
        if tp.tp == ETimePoint.RESET_TIMES:
            return tp.args is self.scr_arg
        return False

    def execute(self):
        from core.game import TimePoint
        tp = TimePoint(ETimePoint.INFLUENCING, self, [self.scr_arg, 1])
        self.game.enter_time_point(tp)
        if tp.args[-1]:
            self.scr_arg.attack_times += 1


class E3(EffSingleStgE3Mixin):
    def __init__(self, host, c, ef):
        super().__init__(host=host, scr_arg=[c, ef])

    def execute(self):
        if self.scr_arg[1] is not None:
            self.scr_arg[0].remove_effect(self.scr_arg[1])
        self.host.remove_effect(self)


class E1(EffSingleStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self, True)
        if tgt is not None:
            from core.game import TimePoint
            tp = TimePoint(ETimePoint.INFLUENCING, self, [self.scr_arg, 1])
            self.game.enter_time_point(tp)
            if tp.args[-1]:
                tgt.attack_times += 1
            e5 = E4(self.host, tgt)
            tgt.register_effect(e5, True)
            e3 = E3(self.host, tgt, e5)
            self.host.register_effect(e3)
            self.host.register_effect(EffSingleStgE2(self.host, [tgt]))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
