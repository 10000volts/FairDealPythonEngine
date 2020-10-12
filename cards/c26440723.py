# 大休假
from utils.common_effects import EffCommonStrategy
from utils.constants import EEffectDesc, ELocation, ETimePoint
from core.game import TimePoint


class E1(EffCommonStrategy):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2HAND, host=host, scr_arg=0)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p1 = self.game.get_player(self.host)
        if self.scr_arg >= 5:
            self.game.send2exiled(p1, p1, self.host, self)
        count = 0
        for p in self.game.players:
            for c in p.on_field:
                if c is not None and c is not self.host:
                    if self.game.send_to(ELocation.HAND + 2 - p.sp, p1, p, c, self, False):
                        if p is p1:
                            count += 1
            p.shuffle()
        if count > 0:
            tp = TimePoint(ETimePoint.TRY_HEAL, self, [self.host, p1.leader, self.host.ATK.value * count, 1])
            self.game.enter_time_point(tp)
            if tp.args[-1]:
                self.game.heal(self.host, p1.leader, self.host.ATK.value * count, self)
        self.scr_arg += 1


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
