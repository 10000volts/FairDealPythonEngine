# 监守自盗的雷西
from core.game import TimePoint
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin

from random import randint


class E2(EffTriggerCostMixin):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.INVALID,
                         host=c, trigger=True, force=True, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TRY_SUMMON:
            return (tp.args[0] is self.host) & (tp.sender is not None)
        return False

    def execute(self):
        # 禁止入场。
        self.reacted.pop().args[-1] = 0


class E1(EffTriggerCostMixin):
    """
    随机丢弃手牌。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DISCARD, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_END:
            if (self.host.location & ELocation.ON_FIELD) > 0:
                for c in self.game.get_player(self.host).hand:
                    tp = TimePoint(ETimePoint.TRY_DISCARD, self, [c, False, 1])
                    self.game.enter_time_point(tp)
                    if tp.args[-1]:
                        return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        # todo: 不会出现不能被丢弃的卡。
        if len(p.hand):
            amin = p.hand[0].ATK.add_val
            for c in p.hand:
                amin = min(c.ATK.add_val, amin)
            cs = list()
            for c in p.hand:
                if c.ATK.add_val == amin:
                    cs.append(c)
            i = randint(0, len(cs) - 1)
            self.game.discard(p, p, cs[i], self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
