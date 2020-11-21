# 黄钻看门人
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, ETimePoint
from utils.common_effects import EffTriggerCostMixin


class E2(Effect):
    """
    常规入场时舍弃手牌。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.SEND2GRAVE,
                         host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUMMONING:
            if (tp.args[0] is self.host) & (tp.sender is None):
                for c in self.game.get_player(self.host).hand:
                    if c is not self.host:
                        tp = TimePoint(ETimePoint.IN_GRAVE, self, [c, 1])
                        self.game.enter_time_point(tp)
                        if tp.args[-1]:
                            return True
        return False

    def cost(self, tp):
        if tp.tp == ETimePoint.SUMMONING:
            p = self.game.get_player(self.host)
            self.reacted.append(tp)
            return self.game.req4discard(p, self.game.players[p.sp], 1, self) is None
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
            if (tp.sender is None) & (tp.args[0] is self.host):
                for c in self.game.get_player(self.host).hand:
                    if c is not self.host:
                        tp = TimePoint(ETimePoint.IN_GRAVE, self, [c, 1])
                        self.game.enter_time_point(tp)
                        if tp.args[-1]:
                            return False
                return True
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
