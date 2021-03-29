# 腐败官员
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin


class E1(EffTriggerCostMixin):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=c, trigger=True, force=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.HEALING:
            # 自己在
            if ((self.host.location & ELocation.ON_FIELD) > 0) | ((self.host.location & ELocation.GRAVE) > 0):
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        tp = self.reacted.pop()
        v = int(tp.args[2] / 2)
        self.host.ATK.gain(v, False, self)
        tp.args[2] -= v


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
