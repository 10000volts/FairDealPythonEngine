# 大举报
from utils.common_effects import EffCommonStrategy
from utils.constants import EEffectDesc, ECardType, ELocation, ETimePoint
from core.game import TimePoint


class E1(EffCommonStrategy):
    """
    丢弃手牌。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DISCARD, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return (c.location == ELocation.HAND + 2 - p.sp) & (c.ATK.value == self.host.ATK.value) & \
                   (c.type == ECardType.EMPLOYEE)

        p = self.game.get_player(self.host)
        for c in p.hand:
            tp = TimePoint(ETimePoint.TRY_DISCARD, self, [c, 1])
            self.game.enter_time_point(tp)
            if tp.args[-1]:
                tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
                if tgt is not None:
                    self.game.discard(p, p, tgt, self)
                break
        p = self.game.players[p.sp]
        for c in p.hand:
            tp = TimePoint(ETimePoint.TRY_DISCARD, self, [c, 1])
            self.game.enter_time_point(tp)
            if tp.args[-1]:
                tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
                if tgt is not None:
                    self.game.discard(p, p, tgt, self)
                break


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
