# 艾登
from utils.common_effects import EffLazyTriggerCostMixin
from utils.constants import EEffectDesc, EGamePhase, ETimePoint


class E1(EffLazyTriggerCostMixin):
    """
    附加值变成+1200。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ADDV_CHANGE, act_phase=EGamePhase.EXTRA_DATA,
                         host=c, trigger=True, force=True, secret=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        return tp.tp == ETimePoint.EXTRA_DATA_GENERATING and tp.args is self.host

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        self.host.ATK.change_adv(1200)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
