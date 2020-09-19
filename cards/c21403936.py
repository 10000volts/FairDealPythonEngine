# 成功之子
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin


class E4(EffTriggerCostMixin):
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


class E3(EffTriggerCostMixin):
    """
    回复生命。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.HEAL, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_END:
            return (self.host.location & ELocation.ON_FIELD) > 0
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        tp = TimePoint(ETimePoint.TRY_HEAL, self, [self.host, p.leader, int(self.host.ATK.value / 5), 1])
        self.game.enter_time_point(tp)
        if tp.args[-1]:
            self.game.heal(self.host, p.leader, int(self.host.ATK.value / 5), self)


class E2(Effect):
    """
    常规入场时支付生命力。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.HP_COST,
                         host=c, trigger=True, force=True, scr_arg=1)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUMMONING:
            if (tp.args[0] is self.host) & (tp.sender is None):
                p = self.game.get_player(self.host)
                tp2 = TimePoint(ETimePoint.TRY_HP_COST, self, [p, self.host.ATK.value, 1])
                self.game.enter_time_point(tp2)
                if tp2.args[-1] & (p.leader.DEF.value > tp2.args[1]):
                    return True
        return False

    def cost(self, tp):
        if tp.tp == ETimePoint.SUMMONING:
            if tp not in self.reacted:
                p = self.game.get_player(self.host)
                self.reacted.append(tp)
                # 支付生命力
                f = p.leader.hp_cost(self.host.ATK.value, self)
                if next(f):
                    next(f)
                    return False
                return True
        return False

    def execute(self):
        # 禁止入场。
        self.reacted.pop().args[-1] = 0


class E1(EffTriggerCostMixin):
    """
    支付生命力检查。
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
                p = self.game.get_player(self.host)
                tp2 = TimePoint(ETimePoint.TRY_HP_COST, self, [p, self.host.ATK.value, 1])
                self.game.enter_time_point(tp2)
                if tp2.args[-1] & (p.leader.DEF.value > tp2.args[1]):
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
    c.register_effect(E3(c))
    c.register_effect(E4(c))
