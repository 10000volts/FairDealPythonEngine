# 成功之子
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin


class E3(EffTriggerCostMixin):
    """
    回复生命。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.HEAL, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_END:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (tp not in self.reacted):
                return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        tp = TimePoint(ETimePoint.TRY_HEAL, self, [self.host, p.leader, 500, 1])
        self.game.enter_time_point(tp)
        if tp.args[-1]:
            self.game.heal(self.host, p.leader, 500, self)


class E2(EffTriggerCostMixin):
    """
    不能通过自身效果以外的方式常规入场。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.INVALID, act_phase=EGamePhase.PLAY_CARD,
                         host=c, trigger=True, force=True, scr_arg=1, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TRY_SUMMON:
            if (tp.args[0] is self.host) & \
                    (tp.sender is None) & self.scr_arg & (tp not in self.reacted):
                return True
        return False

    def execute(self):
        # 禁止入场。
        self.reacted.pop().args[-1] = 0


class E1(Effect):
    """
    支付生命力以常规入场。
    """
    def __init__(self, c, ef):
        super().__init__(desc=EEffectDesc.SUMMON, host=c, scr_arg=ef)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.ASK4EFFECT and tp not in self.reacted:
            p = self.game.get_player(self.host)
            if self.host in p.hand:
                tp2 = TimePoint(ETimePoint.TRY_HP_COST, self, [p, 5000, 1])
                self.game.enter_time_point(tp2)
                if tp2.args[-1] & (p.leader.DEF.value > tp2.args[1]):
                    if p.summon_times == 0:
                        return False
                    for posture in range(0, 2):
                        for pos in range(0, 3):
                            if p.on_field[pos] is None:
                                self.scr_arg.scr_arg = 0
                                tp = TimePoint(ETimePoint.TRY_SUMMON, None, [self.host, p, pos, posture, 1])
                                self.game.enter_time_point(tp)
                                # 入场被允许
                                if tp.args[-1]:
                                    self.scr_arg.scr_arg = 1
                                    return True
        return False

    def cost(self, tp):
        """
        支付cost，触发式效果需要在此添加连锁到的时点(且必须在进入新的时点前)。
        :return:
        """
        sd = self.game.get_player(self.host)
        if self.condition(tp):
            self.reacted.append(tp)
            # 支付一半生命力
            f = sd.leader.hp_cost(5000, self)
            if next(f):
                next(f)
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 常规入场
        p = self.game.get_player(self.host)
        self.scr_arg.scr_arg = 0
        self.game.common_summon(p, p, self.host)
        self.scr_arg.scr_arg = 1


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e2 = E2(c)
    c.register_effect(e2)
    c.register_effect(E1(c, e2))
    c.register_effect(E3(c))
