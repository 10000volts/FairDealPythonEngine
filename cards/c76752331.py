# 你的超人老爹
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, ELocation, ECardType
from utils.common_effects import EffAttackLimit, EffTriggerCostMixin


class E4(EffAttackLimit):
    """
    不能直接攻击
    """
    def __init__(self, c):
        super().__init__(host=c, can_invalid=False)


class E3(EffTriggerCostMixin):
    """
    受到的伤害减半。
    """
    def __init__(self, c, p):
        super().__init__(desc=EEffectDesc.DAMAGE_CHANGE, act_phase=EGamePhase.PLAY_CARD,
                         host=c, trigger=True, force=True, scr_arg=p, no_reset=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEALING_DAMAGE and tp.args[1] is self.scr_arg and tp not in self.reacted:
            return True
        return False

    def execute(self):
        # 输出
        super().execute()
        tp = self.reacted.pop()
        tp.args[2] = int(tp.args[2] / 2)


class E2(Effect):
    """
    从手牌入场。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, act_phase=EGamePhase.PLAY_CARD,
                         host=c)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.ASK4EFFECT:
            sd = self.game.get_player(self.host)
            if (sd.leader.DEF.value > 1000) | (self.host not in sd.hand):
                return False
            for posture in range(0, 2):
                for pos in range(0, 3):
                    if sd.on_field[pos] is None:
                        tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, sd, pos, posture, 1])
                        self.game.enter_time_point(tp)
                        # 入场被允许
                        return tp.args[-1]
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()
        # 从手牌入场
        if self.host.location & ELocation.HAND:
            p = self.game.get_player(self.host)
            self.game.special_summon(p, p, self.host, self)
            # 我方受到的伤害减半
            e3 = E3(self.host, p.leader)
            self.host.register_effect(e3, True)


class E1(EffTriggerCostMixin):
    """
    不能通过自身效果以外的方式入场。
    """
    def __init__(self, c, ef):
        super().__init__(desc=EEffectDesc.INVALID, act_phase=EGamePhase.PLAY_CARD,
                         host=c, trigger=True, force=True, scr_arg=ef)

    def condition(self, tp):
        if tp.tp == ETimePoint.TRY_SUMMON:
            if (tp.args[0] is self.host) & \
                    (tp.sender is self.scr_arg) & (tp not in self.reacted):
                return True
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
    c.register_effect(E4(c))
