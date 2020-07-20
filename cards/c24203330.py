# 空手道练习者
from core.game import TimePoint
from utils.constants import EEffectDesc, ETimePoint, ECardType, ELocation
from utils.common_effects import EffCommonSummon


class E1(EffCommonSummon):
    """
    改变场上1雇员至防御姿态。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.CHANGE_POSTURE, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()

        def check(c):
            if ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE):
                tp = TimePoint(ETimePoint.TRY_CHANGE_POSTURE, self, [c, 1])
                self.game.enter_time_point(tp)
                return tp.args[-1]
        tgt = self.game.choose_target(check, self)
        if tgt is not None:
            self.game.change_posture(self.game.get_player(self.host), tgt, 1)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
