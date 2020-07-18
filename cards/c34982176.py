# 奇利亚诺
from core.game import TimePoint
from utils.constants import EEffectDesc, ETimePoint, ECardType, ELocation
from utils.common_effects import EffCommonSummon


class E1(EffCommonSummon):
    """
    交换场上1雇员的属性。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()

        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        tgt = self.game.choose_target(check, self)
        if tgt is not None:
            atk = tgt.ATK.value
            tgt.ATK.become(tgt.DEF.value)
            tgt.DEF.become(atk)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
