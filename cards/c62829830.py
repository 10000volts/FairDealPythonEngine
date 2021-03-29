# 对现状的恐惧
from random import randint

from utils.common_effects import EffTriggerCostMixin
from core.game import GameCard, ETimePoint, Effect
from utils.constants import EEffectDesc, ELocation


class E2(Effect):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DISCARD, host=host)

    def condition(self, tp):
        if tp.tp == ETimePoint.ASK4EFFECT:
            return (self.host.location & ELocation.GRAVE) > 0
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        self.game.send2exiled(p, p, self.host, self)
        cs = list()
        for c in p.hand:
            if '冥思' in c.series:
                cs.append(c)
        for i in range(0, 3):
            if len(cs) > 0:
                c = cs[randint(0, len(cs) - 1)]
                self.game.discard(p, p, c, self)
                cs.remove(c)
            else:
                return


class E1(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2HAND, host=host)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        return tp is None

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)
        for i in range(0, 2):
            c = GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '87032772', is_token=True)
            c.ATK.become(self.host.ATK.value, False, self)
            self.game.send2hand(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
