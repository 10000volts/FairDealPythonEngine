# 现金流
from core.game import TimePoint
from utils.common_effects import EffCommonStrategy, EffNextTurnMixin
from utils.constants import EEffectDesc, ETimePoint


class E2(EffNextTurnMixin):
    """
    回合开始时回复攻击力(2次)，之后失去4000生命力。
    """
    def __init__(self, host, c, v):
        super().__init__(desc=EEffectDesc.HEAL,
                         host=host, trigger=True, force=True, scr_arg=[c, v, 0], no_reset=True)

    def execute(self):
        tp = TimePoint(ETimePoint.TRY_HEAL, self, [self.host, self.scr_arg[0], self.scr_arg[1], 1])
        self.game.enter_time_point(tp)
        if self.scr_arg[2] < 1:
            if tp.args[-1]:
                self.game.heal(self.host, self.scr_arg[0], self.scr_arg[1], self)
            self.scr_arg[2] += 1
        else:
            if self.scr_arg[0].DEF.value > 3000:
                self.scr_arg[0].DEF.gain(-3000, False, self)
            else:
                self.description = EEffectDesc.EFFECT_END
                self.scr_arg[0].DEF.become(1, False, self)
            self.host.remove_effect(self)


class E1(EffCommonStrategy):
    """
    回复5000生命力并增加额外效果。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.HEAL, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)
        tp = TimePoint(ETimePoint.TRY_HEAL, self, [self.host, p.leader, 3000, 1])
        self.game.enter_time_point(tp)
        if tp.args[-1]:
            self.game.heal(self.host, p.leader, 3000, self)
        self.host.register_effect(E2(self.host, p.leader, self.host.ATK.value))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
