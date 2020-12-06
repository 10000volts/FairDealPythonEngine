# 暴走族骑手
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin
from core.game import GameCard


class E3(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2DECK, host=host, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            if tp.args[1] is self.host:
                return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        c = GameCard(self.game, ELocation.UNKNOWN + 2 - p.sp, '66263624', is_token=True)
        self.game.send2deck(p, p, c, self)


class E2(Effect):
    """
    常规入场时手牌回到卡组。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.SEND2DECK,
                         host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUMMONING:
            if (tp.args[0] is self.host) & (tp.sender is None):
                p = self.game.get_player(self.host)
                count = 0
                for c in self.game.get_player(self.host).hand:
                    if c is not self.host:
                        count += 1
                        if count >= 2:
                            return True
                return False
        return False

    def cost(self, tp):
        if tp.tp == ETimePoint.SUMMONING:
            def check(c):
                return (c.location == ELocation.HAND + 2 - p.sp) & (c is not self.host)

            p = self.game.get_player(self.host)
            self.reacted.append(tp)
            tgts = self.game.choose_target_from_func(p, p, check, self, False, False, 2)
            if tgts is not None:
                for tgt in tgts:
                    self.game.send2deck(p, p, tgt, self)
                return True
        return False

    def execute(self):
        # 禁止入场。
        self.reacted.pop().args[-1] = 0


class E1(EffTriggerCostMixin):
    """
    检查。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.INVALID, host=c, trigger=True, force=True,
                         passive=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.TRY_SUMMON:
            if (tp.args[0] is self.host) & (tp.sender is None):
                p = self.game.get_player(self.host)
                count = 0
                for c in self.game.get_player(self.host).hand:
                    if c is not self.host:
                        count += 1
                        if count >= 2:
                            return True
                return False
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 无效化入场
        self.reacted.pop().args[-1] = 0


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
    c.register_effect(E3(c))
