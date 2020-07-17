from models.effect import Effect
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, ECardType
from utils.common import adj_pos


class EffInvestigator(Effect):
    """
    调查筹码的效果。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.INVESTIGATE, act_phase=EGamePhase.PUT_CARD,
                         host=host, trigger=True, force=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if (tp.tp == ETimePoint.CARD_PUT) and (tp.args[2] is self.host) \
                and (tp not in self.reacted):
            return True
        return False

    def cost(self, tp):
        """
        支付cost，触发式效果需要在此添加连锁到的时点(且必须在进入新的时点前)。
        :return:
        """
        if self.condition(tp):
            self.reacted.append(tp)
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
                    g.show_card(sd, g.chessboard[c].vid, self)
        self.host.remove_effect(self)


class EffTriggerCostMixin(Effect):
    """
    默认的触发式效果cost行为。
    """
    def cost(self, tp):
        if self.condition(tp):
            self.reacted.append(tp)
            return True
        return False


class EffNextTurnMixin(EffTriggerCostMixin):
    """
    到自己的下回合时发动
    """
    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_BEGIN and self.game.turn_player is self.game.get_player(self.host) \
                and tp not in self.reacted:
            return True
        return False


class EffTurnEndMixin(EffTriggerCostMixin):
    """
    到回合结束时发动
    """
    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_END and tp not in self.reacted:
            return True
        return False


class EffUntil(Effect):
    """
    满足条件时删除效果。
    """
    def __init__(self, host, ef, until):
        super().__init__(desc=EEffectDesc.REMOVE_EFFECT, act_phase=EGamePhase.PLAY_CARD,
                         host=host, trigger=True, force=True, scr_arg=ef, no_reset=True)
        self.until = until

    def condition(self, tp):
        if self.until(tp) and tp not in self.reacted:
            return True
        return False

    def cost(self, tp):
        if self.condition(tp):
            self.reacted.append(tp)
            return True
        return False

    def execute(self):
        self.host.remove_effect(self.scr_arg)
        self.host.remove_effect(self)


class EffAttackLimit(Effect):
    """
    不能直接攻击
    """
    def __init__(self, host, can_invalid):
        super().__init__(desc=EEffectDesc.INVALID, act_phase=EGamePhase.PLAY_CARD,
                         host=host, trigger=True, force=True, can_invalid=can_invalid)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.TRY_ATTACK:
            # 攻击者是自己
            if (tp.args[1].type == ECardType.LEADER) & (tp.args[0] is self.host) & (tp not in self.reacted):
                return True
        return False

    def cost(self, tp):
        if self.condition(tp):
            self.reacted.append(tp)
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
            if (tp.args[1] is self.host) & (tp not in self.reacted):
                return True
        return False

    def cost(self, tp):
        if self.condition(tp):
            self.reacted.append(tp)
            return True
        return False

    def execute(self):
        super().execute()
        # 无效摧毁
        self.reacted.pop().args[-1] = 0


class EffProtectProtocol(Effect):
    """
    保护协议(破产保护)
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.PROTECT_PROTOCOL, act_phase=EGamePhase.PLAY_CARD,
                         host=host, trigger=True)

    def condition(self, tp):
        # 自己的回合，雇员以防御姿态在自己场上入场后
        p = self.game.get_player(self.host)
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if (self.game.turn_player is p) & (tp.args[0] in p.on_field) &\
                    (tp.args[2]) & (tp not in self.reacted):
                return True
        return False

    def cost(self, tp):
        if self.condition(tp):
            self.reacted.append(tp)
            return True
        return False

    def execute(self):
        # 输出
        super().execute()

        c = self.reacted.pop().args[0]
        e = EffProtect(c, False)
        # 直到下次我方回合开始时不会被摧毁
        c.register_effect(e, True)
        c.register_effect(EffUntil(c, e,
                                   lambda tp: ((tp.tp == ETimePoint.TURN_BEGIN) &
                                               (self.game.turn_player is self.game.get_player(self.host)))))
        # 可无限次阻挡
        c.block_times = -1
        # 不能直接攻击
        c.register_effect(EffAttackLimit(c, False))
        # 全局1次
        self.host.remove_effect(self)


class EffPerTurn(EffTriggerCostMixin):
    """
    每回合1次的效果。
    """

    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.RESET_TIMES, host=host, trigger=True, force=True,
                         scr_arg=ef)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.TURN_BEGIN:
            if tp not in self.reacted:
                return True
        return False

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
    def __init__(self, desc, host):
        super().__init__(desc=desc, act_phase=EGamePhase.PLAY_CARD, host=host)

    def condition(self, tp):
        return tp is None


class EffSummon(Effect):
    """
    入场后效果模板。
    """
    def __init__(self, desc, host):
        super().__init__(desc=desc, act_phase=EGamePhase.PLAY_CARD,
                         host=host, trigger=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.SUCC_SUMMON and tp.args[0] is self.host and tp not in self.reacted:
            return True
        return False

    def cost(self, tp):
        """
        支付cost，触发式效果需要在此添加连锁到的时点(且必须在进入新的时点前)。
        :return:
        """
        if self.condition(tp):
            self.reacted.append(tp)
            return True
        return False


class EffCommonSummon(Effect):
    """
    常规入场后效果模板。
    """
    def __init__(self, desc, host):
        super().__init__(desc=desc, act_phase=EGamePhase.PLAY_CARD,
                         host=host, trigger=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.SUCC_SUMMON and tp.args[0] is self.host and tp not in self.reacted \
                and tp.sender is None:
            return True
        return False

    def cost(self, tp):
        """
        支付cost，触发式效果需要在此添加连锁到的时点(且必须在进入新的时点前)。
        :return:
        """
        if self.condition(tp):
            self.reacted.append(tp)
            return True
        return False
