# 兄贵三兄弟
from core.game import TimePoint, GameCard
from utils.constants import EEffectDesc, EEmployeeType, ETimePoint, ECardType, ECardRank, ELocation
from utils.common_effects import EffCommonSummon


class E1(EffCommonSummon):
    """
    特召。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=c)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)
        for i in range(0, 2):
            c = GameCard(self.game, ELocation.UNKNOWN + 2 - p.sp)
            c.create('另外两兄弟', ECardType.EMPLOYEE, EEmployeeType.COMMON, ECardRank.TRUMP,
                     1500, 0)
            for posture in range(0, 2):
                pos = 0
                while pos in range(0, 3):
                    if p.on_field[pos] is None:
                        tp = TimePoint(ETimePoint.TRY_SUMMON, self, [c, p, pos, posture, 1])
                        self.game.enter_time_point(tp)
                        if tp.args[-1]:
                            self.game.special_summon(p, p, c, self)
                            # 跳出循环
                            pos = 3
                    pos += 1
                else:
                    break


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
