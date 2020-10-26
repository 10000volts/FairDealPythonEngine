from models.effect import Effect
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, ECardType, ELocation
from utils.common import adj_pos


class EffTriggerCostMixin(Effect):
    """
    默认的触发式效果cost行为。
    """
    def cost(self, tp):
        if tp not in self.reacted:
            self.reacted.append(tp)
            return True
        return False


class EffInvestigator(EffTriggerCostMixin):
    """
    调查筹码的效果。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.INVESTIGATE, act_phase=EGamePhase.PUT_CARD,
                         host=host, trigger=True, force=True, passive=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if (tp.tp == ETimePoint.CARD_PUT) and (tp.args[2] is self.host):
            return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        g = self.game
        tp = self.reacted.pop()
        x = tp.args[0]
        y = tp.args[1]
        cs = adj_pos(x, y, g.scale)
        # 展示其中的对方卡
        sd = self.game.get_player(self.host)
        for c in cs:
            if g.chessboard[c] is not None:
                if (g.chessboard[c].location - sd.sp) % 2:
                    g.investigate(sd, g.chessboard[c].vid, c)
        self.host.remove_effect(self)


class EffTurnCostMixin(Effect):
    """
    默认的回合限定cost行为。
    """
    def cost(self, tp):
        if self.condition(tp):
            p = self.game.get_player(self.host)
            if self.ef_id in self.game.ef_listener:
                p.ef_limiter[self.ef_id] += 1
            else:
                p.ef_limiter[self.ef_id] = 1
            return True
        return False


class EffCostMixin(Effect):
    """
    默认的cost行为。
    """
    def cost(self, tp):
        return self.condition(tp)


class EffLazyTriggerCostMixin(Effect):
    """
    默认的触发式效果cost行为。
    """
    def cost(self, tp):
        if tp not in self.reacted:
            self.reacted.append(tp)
            return True
        return False


class EffNextTurnMixin(EffLazyTriggerCostMixin):
    """
    到自己的下回合时发动
    """
    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_BEGIN and self.game.turn_player is self.game.get_player(self.host):
            return True
        return False


class EffTurnEndMixin(EffLazyTriggerCostMixin):
    """
    到回合结束时发动
    """
    def condition(self, tp):
        return tp.tp == ETimePoint.TURN_END


class EffUntil(EffTriggerCostMixin):
    """
    满足条件时删除效果。
    """
    def __init__(self, host, ef, until):
        super().__init__(desc=EEffectDesc.REMOVE_EFFECT,
                         host=host, trigger=True, force=True, scr_arg=ef, no_reset=True, passive=True)
        self.until = until

    def condition(self, tp):
        return self.until(tp)

    def execute(self):
        self.host.remove_effect(self.scr_arg)
        self.host.remove_effect(self)


class EffAttackLimit(EffTriggerCostMixin):
    """
    不能直接攻击
    """
    def __init__(self, host, can_invalid):
        super().__init__(desc=EEffectDesc.INVALID, act_phase=EGamePhase.PLAY_CARD,
                         host=host, trigger=True, force=True, can_invalid=can_invalid,
                         passive=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.TRY_ATTACK:
            # 攻击者是自己
            if (tp.args[1].type == ECardType.LEADER) & (tp.args[0] is self.host):
                return True
        return False

    def execute(self):
        # 无效
        self.reacted.pop().args[-1] = 0


class EffProtect(Effect):
    """
    不会被摧毁。
    """
    def __init__(self, host, can_invalid):
        super().__init__(desc=EEffectDesc.PROTECT_PROTOCOL, act_phase=EGamePhase.PLAY_CARD,
                         host=host, trigger=True, force=True, can_invalid=can_invalid)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYING:
            return tp.args[1] is self.host
        return False

    def cost(self, tp):
        if tp not in self.reacted:
            self.reacted.append(tp)
            return True
        return False

    def execute(self):
        # 无效摧毁
        self.reacted.pop().args[-1] = 0


class EBattleDamage0(EffLazyTriggerCostMixin):
    """
    伤害变成0
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DAMAGE_CHANGE, host=c, can_invalid=False, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEALING_DAMAGE:
            if tp.args[0] == self.host:
                return True
        return False

    def execute(self):
        self.reacted.pop().args[2] = 0


class EffProtectProtocol(Effect):
    """
    保护协议(破产保护)
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.PROTECT_PROTOCOL, host=host)

    def condition(self, tp):
        if tp.tp == ETimePoint.ASK4EFFECT:
            p = self.game.get_player(self.host)
            for c in p.on_field:
                if c is not None and c.type == ECardType.EMPLOYEE:
                    return True
        return False

    def execute(self):
        def check(c):
            return (c.location == ELocation.ON_FIELD + 2 - p.sp) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, check, self)
        e = EffProtect(tgt, False)
        # 直到下次我方回合开始时不会被摧毁
        tgt.register_effect(e, True)
        tgt.register_effect(EffUntil(tgt, e,
                                     lambda tp: ((tp.tp == ETimePoint.TURN_BEGIN) &
                                               (self.game.turn_player is self.game.get_player(self.host)))))
        # 可无限次阻挡
        tgt.block_times = -1
        # 战斗伤害变成0
        tgt.register_effect(EBattleDamage0(tgt))
        # 全局1次
        self.host.remove_effect(self)


class EffPerTurn(EffLazyTriggerCostMixin):
    """
    每回合1次的效果。
    """

    def __init__(self, host, ef, **kwargs):
        super().__init__(desc=EEffectDesc.RESET_TIMES, host=host, trigger=True, force=True,
                         scr_arg=ef, **kwargs)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        return (tp.tp == ETimePoint.TURN_BEGIN) & ((self.host.location & ELocation.ON_FIELD) > 0)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        if self.scr_arg not in self.host.effects:
            self.host.register_effect(self.scr_arg)


class EffCommonStrategy(Effect):
    """
    常规策略的缺省效果。
    """
    def __init__(self, desc, host, **kwargs):
        super().__init__(desc=desc, host=host, **kwargs)

    def condition(self, tp):
        return tp is None


class EffCounterStgE1Mixin(EffLazyTriggerCostMixin):
    """
    反制策略的E2效果，用来触发其真正效果。请将passive置为True。
    """
    def condition(self, tp):
        return tp is not None and tp.tp != ETimePoint.ASK4EFFECT


class EffExile(Effect):
    """
    以从场下移除作为COST。
    """
    def condition(self, tp):
        if tp.tp == ETimePoint.ASK4EFFECT:
            # todo: 不会做禁止场下移除的效果。
            return (self.host.location & ELocation.GRAVE) > 0

    def cost(self, tp):
        p = self.game.get_player(self.host)
        return self.game.send2exiled(p, p, self.host, self)


class EffCounterStgE2Mixin(EffTriggerCostMixin):
    """
    反制策略的E2效果，用来触发其真正效果。
    """
    def execute(self):
        from core.game import TimePoint
        tp = TimePoint(ETimePoint.UNCOVERING_STRATEGY, None, [self.host, 1])
        self.game.enter_time_point(tp)
        if tp.args[-1]:
            p = self.game.get_player(self.host)
            # 向真正的效果传递时点信息
            self.scr_arg[0].scr_arg[0] = self.reacted.pop()
            self.game.activate_strategy(p, p, self.host, self.host.inf_pos)
        self.game.enter_time_point(TimePoint(ETimePoint.UNCOVERED_STRATEGY, None, [self.host]))

    def cost(self, tp):
        if super().cost(tp):
            self.host.cover = 0
            return True
        return False


class EffSingleStgE1Mixin(EffTriggerCostMixin):
    """
    单人策略的E1效果模板，代表其发动时必须指定1目标。
    """
    def condition(self, tp):
        from core.game import TimePoint
        if tp is None:
            # 场上存在可以成为效果对象的雇员
            for p in self.game.players:
                for c in p.on_field:
                    if c is not None:
                        if c.type == ECardType.EMPLOYEE:
                            # 模拟选择。
                            t = TimePoint(ETimePoint.TRY_CHOOSE_TARGET, self, [c, 1])
                            self.game.enter_time_point(t)
                            if t.args[-1]:
                                return True
        return False


class EffSingleStgE2(EffLazyTriggerCostMixin):
    """
    单人策略的E2效果，代表其所属雇员离场后其送去场下。
    """
    def __init__(self, host, scr_arg):
        super().__init__(desc=EEffectDesc.SEND2GRAVE, host=host, trigger=True,
                         force=True, can_invalid=False, scr_arg=scr_arg, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.OUT_FIELD_END:
            return tp.args[0] is self.scr_arg[0]
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        self.game.send_to_grave(p, p, self.host)


class EffSingleStgE3Mixin(EffLazyTriggerCostMixin):
    """
    单人策略的E3效果，代表送去场下后移除之前生效的效果。
    """
    def __init__(self, host, scr_arg):
        super().__init__(desc=EEffectDesc.EFFECT_END, host=host, trigger=True,
                         force=True, scr_arg=scr_arg, passive=True, no_reset=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.OUT_FIELD_END:
            return tp.args[0] is self.host
        return False


class EffSummon(EffLazyTriggerCostMixin):
    """
    入场后效果模板。
    """
    def __init__(self, desc, host, **kwargs):
        super().__init__(desc=desc, act_phase=EGamePhase.PLAY_CARD,
                         host=host, trigger=True, **kwargs)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        return tp.tp == ETimePoint.SUCC_SUMMON and tp.args[0] is self.host


class EffCommonSummon(EffTriggerCostMixin):
    """
    常规入场后效果模板。
    """
    def __init__(self, desc, host, **kwargs):
        super().__init__(desc=desc, host=host, trigger=True, **kwargs)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.SUCC_SUMMON and tp.args[0] is self.host\
                and tp.sender is None:
            return True
        return False


class EffPierce(EffLazyTriggerCostMixin):
    """
    穿透。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.PIERCE, host=host, trigger=True, force=True,
                         ef_id=EEffectDesc.PIERCE)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.ATTACK_DAMAGE_JUDGE and tp.args[0] is self.host:
            return True
        return False

    def execute(self):
        tp = self.reacted.pop()
        # 修改战斗伤害
        tp.args[2] = self.host.ATK.value
        # 防御姿态
        if tp.args[1].posture:
            tp.args[2] -= tp.args[1].DEF.value
        else:
            tp.args[2] -= tp.args[1].ATK.value


class EffTaunt(EffTriggerCostMixin):
    """
    嘲讽。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.TAUNT, host=host, trigger=True, force=True, passive=True,
                         ef_id=EEffectDesc.TAUNT)

    def condition(self, tp):
        from core.game import TimePoint
        # 是在尝试攻击的时点，所以被阻挡(攻击时时点)不会发生问题。
        if tp.tp == ETimePoint.TRY_ATTACK:
            p = self.game.get_player(self.host)
            op = self.game.players[p.sp]
            if (tp.args[0] in op.on_field) & (self.host in p.on_field) & (self.host.cover == 0):
                for ef in tp.args[1].effects:
                    if ef.ef_id == EEffectDesc.TAUNT:
                        return False
                # 必须可被选择为攻击对象。
                tp = TimePoint(ETimePoint.TRY_ATTACK, self, [tp.args[0], self.host, 1])
                for ef in self.host.effects:
                    if ef.ef_id != EEffectDesc.TAUNT:
                        if ef.condition(tp):
                            ef.execute()
                return tp.args[-1]
        return False

    def execute(self):
        self.reacted.pop().args[-1] = 0


class EffAgile(EffLazyTriggerCostMixin):
    """
    风行。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.AGILE, host=host, trigger=True, force=True,
                         passive=True)

    def condition(self, tp):
        return tp.tp == ETimePoint.CHARGE_CHECK

    def execute(self):
        self.host.charge = True


class EffHPLimit(EffLazyTriggerCostMixin):
    """
    血量上限。
    """
    def __init__(self, host, limit=10000):
        super().__init__(desc=EEffectDesc.FORBIDDEN, host=host, trigger=True, force=True,
                         passive=True, scr_arg=limit, ef_id=EEffectDesc.DISCARD_OVERFLOW,
                         can_invalid=False)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEF_CALCING:
            if (tp.args[0] is self.host) & (tp.args[1] > self.scr_arg):
                return True
        return False

    def execute(self):
        tp = self.reacted.pop()
        if tp.args[1] >= self.scr_arg:
            tp.args[1] = self.scr_arg
