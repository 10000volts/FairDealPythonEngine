# 传奇骇客
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, ELocation, ECardType
from utils.common_effects import EffTriggerCostMixin, EffSummon, EffUntil


class E1(EffTriggerCostMixin):
    """
    回合结束时造成伤害。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host, trigger=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.TURN_END:
            p = self.game.get_player(self.host)
            # 是我方回合，在场
            if (self.game.turn_player is self.game.get_player(self.host)) & (self.host in p.on_field) & \
                    (tp not in self.reacted):
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)
        self.game.deal_damage(self.host, self.game.players[p.sp].leader, int(self.host.ATK.value / 2))


class E2(EffTriggerCostMixin):
    """
    对方不能使用策略。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.FORBIDDEN, host=host, trigger=True, force=True, no_reset=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.TRY_ACTIVATE_STRATEGY:
            p = self.game.get_player(self.host)
            # 是对方的策略
            if ((tp.args[0].location & (self.game.get_player(self.host).sp + 1)) > 0) & (tp not in self.reacted):
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 无效
        self.reacted.pop().args[-1] = 0


class E3(EffSummon):
    """
    入场时赋予效果。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.FORBIDDEN, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 赋予效果
        e2 = E2(self.host)
        self.host.register_effect(e2, True)
        self.host.register_effect(EffUntil(self.host, e2, lambda tp: tp.tp == ETimePoint.TURN_END))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E3(c))
