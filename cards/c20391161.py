# 你的超人老妈
from utils.constants import EEffectDesc, ELocation, ECardType, ETimePoint
from utils.common_effects import EffTriggerCostMixin
from core.game import TimePoint


class E1(EffTriggerCostMixin):
    """
    从场下回收。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=host, trigger=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.SUCC_SUMMON and tp.args[0] is self.host\
                and tp.sender is None:
            p = self.game.get_player(self.host)
            for pos in range(0, 3):
                if p.on_field[pos] is None:
                    for c in p.grave:
                        if c.type == ECardType.EMPLOYEE:
                            for posture in range(0, 2):
                                t = TimePoint(ETimePoint.TRY_SUMMON, self, [c, p, pos, posture, 1])
                                self.game.enter_time_point(t)
                                if t.args[-1]:
                                    return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)

        def check(c):
            if (c.location == 2 - p.sp + ELocation.GRAVE) & (c.type == ECardType.EMPLOYEE):
                for pos in range(0, 3):
                    if p.on_field[pos] is None:
                        tp = TimePoint(ETimePoint.TRY_SUMMON, self, [c, p, pos, 1, 1])
                        self.game.enter_time_point(tp)
                        if tp.args[-1]:
                            return True
                return False
        tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
        if tgt is not None:
            self.game.special_summon(p, p, tgt, self, 1)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
