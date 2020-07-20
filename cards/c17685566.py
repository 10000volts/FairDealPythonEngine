# 桶金
from core.game import TimePoint
from utils.common_effects import EffSingleStgE1Mixin
from utils.constants import EEffectDesc, ETimePoint


class E1(EffSingleStgE1Mixin):
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
        # 输出
        super().execute()

        p = self.game.get_player(self.host)
        tp = TimePoint(ETimePoint.TRY_HEAL, self, [self.host, p.leader, self.host.ATK.value, 1])
        self.game.enter_time_point(tp)
        if tp.args[-1]:
            self.game.heal(self.host, p.leader, self.host.ATK.value, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
