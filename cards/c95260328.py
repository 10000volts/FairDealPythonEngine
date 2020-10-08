# 密灵西
from utils.common_effects import EffLazyTriggerCostMixin
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, ELocation


class E1(EffLazyTriggerCostMixin):
    """
    附加值变成+1000。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ADDV_CHANGE, act_phase=EGamePhase.EXTRA_DATA,
                         host=c, trigger=True, secret=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.EXTRA_DATA_GENERATED:
            if (self.host.location & ELocation.HAND) > 0:
                return True
            p = self.game.get_player(self.host)
            for c in p.side:
                if ('水星乐队' in c.series) & (c is not self.host):
                    return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return (self.game.get_player(c) is self.game.get_player(self.host)) & \
                   ((c.location & ELocation.HAND) > 0)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
        if tgt is not None:
            tgt.ATK.change_adv(1000)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
