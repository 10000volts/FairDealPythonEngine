# 防暴警察
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType
from utils.common_effects import EffLazyTriggerCostMixin, EffTriggerCostMixin
from core.game import TimePoint


class E3(EffTriggerCostMixin):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_ENDING:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) \
                    & (self.game.turn_player is self.game.get_player(self.host)):
                return True
        return False

    def execute(self):
        c = self.game.players[self.game.get_player(self.host).sp].on_field[self.host.inf_pos]
        if c is not None:
            c.ATK.gain(-500, False, self)


class E2(EffTriggerCostMixin):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.INVALID, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYING:
            if (tp.args[1] is self.host) & (tp.args[0].type == ECardType.EMPLOYEE) & \
                    ((tp.args[0].location & ELocation.ON_FIELD) > 0) & (tp.args[0].inf_pos == self.host.inf_pos):
                return True
        return False

    def execute(self):
        self.game.invalid_tp(self.reacted.pop(), self.host, self)


class E1(EffLazyTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=host, trigger=True, ef_id='708363660')

    def condition(self, tp):
        if tp.tp == ETimePoint.BLOCKED:
            p = self.game.get_player(self.host)
            if ((tp.args[1].location & (2 - p.sp)) > 0) & (self.host.location == 2 - p.sp + ELocation.HAND) & \
                    (self.ef_id not in p.ef_limiter):
                for pos in range(0, 3):
                    if p.on_field[pos] is None:
                        tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, p, pos, 1, 1])
                        self.game.enter_time_point(tp)
                        # 入场被允许
                        return tp.args[-1] == 1
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 注册效果
        p = self.game.get_player(self.host)
        p.ef_limiter[self.ef_id] = 1
        self.game.special_summon(p, p, self.host, self, 1)
        self.host.register_effect(E2(self.host))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E3(c))