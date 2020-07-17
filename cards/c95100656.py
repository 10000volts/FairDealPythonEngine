# 洛斯
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, ELocation
from utils.common_effects import EffUntil


class E2(Effect):
    """
    对方受到的伤害减半。
    """
    def __init__(self, c, p):
        super().__init__(desc=EEffectDesc.DAMAGE_CHANGE, act_phase=EGamePhase.PLAY_CARD,
                         host=c, trigger=True, force=True, scr_arg=p, no_reset=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEALING_DAMAGE and tp.args[1] is self.scr_arg and tp not in self.reacted:
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
        tp = self.reacted.pop()
        tp.args[2] = int(tp.args[2] / 2)


class E1(Effect):
    """
    从场下入场。
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
            for posture in range(0, 2):
                for pos in range(0, 3):
                    if sd.on_field[pos] is None:
                        tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, pos, posture, 1])
                        self.game.enter_time_point(tp)
                        # 入场被允许
                        if tp.args[-1]:
                            # 在场下
                            if self.host.location & ELocation.GRAVE:
                                # 场上的卡恰好为5张
                                count = 0
                                for i in range(0, 6):
                                    for p in self.game.players:
                                        if p.on_field[i] is not None:
                                            count += 1
                                return count == 5
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()
        # 从场下入场
        if self.host.location & ELocation.GRAVE:
            p = self.game.get_player(self.host)
            self.game.special_summon(p, p, self.host, self)
            # 对方本回合受到的伤害减半
            e2 = E2(self.host, self.game.players[p.sp].leader)
            self.host.register_effect(e2, True)
            self.host.register_effect(EffUntil(self.host, e2,
                                               lambda tp: tp.tp == ETimePoint.TURN_END))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
