# 飞天拉面神
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType
from utils.common_effects import EffPierce, EffTriggerCostMixin, EffNextTurnMixin, EffUntil


class E7(EffTriggerCostMixin):
    """
    不能改变姿态。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.FORBIDDEN, host=host, trigger=True, force=True, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TRY_CHANGE_POSTURE:
            return tp.args[0] is self.host
        return False

    def execute(self):
        self.reacted.pop().args[-1] = 0


class E6(EffTriggerCostMixin):
    """
    遗言。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.OUT_FIELD_END:
            if tp.args[0] is self.host:
                p = self.game.get_player(self.host)
                for c in p.grave:
                    if (c.type == ECardType.EMPLOYEE) & (c.cid != self.host.cid):
                        for pos in range(0, 3):
                            if p.on_field[pos] is None:
                                tp = TimePoint(ETimePoint.TRY_SUMMON, self, [c, p, pos, 1, 1])
                                self.game.enter_time_point(tp)
                                if tp.args[-1]:
                                    return True
        return False

    def execute(self):
        def check(c):
            return (c in p.grave) & (c.cid != self.host.cid) & (c.type == ECardType.EMPLOYEE)

        # 选择的卡特招
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
        if tgt is not None:
            self.game.special_summon(p, p, tgt, self, 1)
            e7 = E7(tgt)
            tgt.register_effect(e7)
            tgt.register_effect(EffUntil(tgt, e7, lambda tp: ((tp.tp == ETimePoint.TURN_BEGIN) &
                                                              (self.game.turn_player is not p))))


class E5(EffNextTurnMixin):
    """
    奉献自身。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DEVOTE, host=host, trigger=True, force=True)

    def execute(self):
        self.game.devote(self.game.get_player(self.host), self.host, self)


class E4(EffTriggerCostMixin):
    """
    造成伤害后赋予自身解放效果。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DISCARD, host=host, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEALT_DAMAGE:
            return (tp.args[0] is self.host) & ((self.host.location & ELocation.ON_FIELD) > 0) & \
                   (tp.args[1] is self.game.players[self.game.get_player(self.host).sp].leader) & \
                   (tp.args[2] > 0)
        return False

    def execute(self):
        op = self.game.players[self.game.get_player(self.host).sp]
        for c in op.hand:
            tp = TimePoint(ETimePoint.TRY_DISCARD, self, [c, True, 1])
            self.game.enter_time_point(tp)
            if tp.args[-1]:
                self.game.req4discard(op, op, 1, self)
                break
        self.host.register_effect(E5(self.host))


class E2(Effect):
    """
    从手牌/场下入场。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=c)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        # todo: 不会设计能无效移除的效果
        def dp(v, i):
            if v == self.host.ATK.value:
                return True
            if i == len(ems):
                return False
            return dp(v + ems[i], i + 1) | dp(v, i + 1)

        if tp.tp == ETimePoint.ASK4EFFECT:
            if self.host.location & (ELocation.HAND | ELocation.GRAVE):
                p = self.game.get_player(self.host)
                for posture in range(0, 2):
                    for pos in range(0, 3):
                        # 不用检查是否有空格子
                        tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, p, pos, posture, 1])
                        self.game.enter_time_point(tp)
                        # 入场被允许
                        if tp.args[-1]:
                            ems = list()
                            for c in p.on_field:
                                if c is not None and c.type == ECardType.EMPLOYEE:
                                    ems.append(c.ATK.value)
                            # 问题规模不需要dp, 过于占用空间
                            return dp(0, 0)
        return False

    def cost(self, tp):
        p = self.game.get_player(self.host)

        def check(_c):
            return (_c in p.on_field) & (_c.type == ECardType.EMPLOYEE)

        return self.game.ceremony(p, check, self.host.ATK.value, ELocation.EXILED,
                                  '=', False)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 入场
        p = self.game.get_player(self.host)
        self.game.special_summon(p, p, self.host, self)


class E1(EffTriggerCostMixin):
    """
    不能通过自身效果以外的方式入场。
    """
    def __init__(self, c, ef):
        super().__init__(desc=EEffectDesc.INVALID,
                         host=c, trigger=True, force=True, scr_arg=ef, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TRY_SUMMON:
            return (tp.args[0] is self.host) & (tp.sender is not self.scr_arg)
        return False

    def execute(self):
        # 禁止入场。
        self.reacted.pop().args[-1] = 0


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e2 = E2(c)
    c.register_effect(e2)
    c.register_effect(E1(c, e2))
    c.register_effect(EffPierce(c, 1000))
    c.register_effect(E4(c))
    c.register_effect(E6(c))
