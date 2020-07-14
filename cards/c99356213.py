# 暴风新人
from utils.common_effects import EffCommonSummon
from utils.constants import EEffectDesc, EGamePhase, ETimePoint


class E1(EffCommonSummon):
    """
    摧毁场上全部策略。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DESTROY, c=c)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()
        # todo: 摧毁场上全部策略


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e1 = E1(c)
    c.register_effect(e1)
