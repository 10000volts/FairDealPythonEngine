# 莱尔 玛斯
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, ECardType, ELocation


class E2(Effect):
    """
    直接攻击时攻击力减半
    """

    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_CHANGE, act_phase=EGamePhase.PLAY_CARD,
                         host=c, trigger=True, force=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.ATTACKING:
            # 自己在场
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (tp.args[1].type == ECardType.LEADER) & \
                    (tp not in self.reacted):
                # 攻击者在对方场上或是自己
                if (tp.args[0] in self.game.players[self.game.get_player(self.host).sp].on_field) \
                        | (tp.args[0] is self.host):
                    return True
        return False

    def cost(self, tp):
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
        # 输出
        super().execute()
        # 攻击力减半
        tp = self.reacted.pop()
        tp.args[0].ATK.plus(0.5)


class E1(Effect):
    """
    场上限定：不会被摧毁。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.INVALID, act_phase=EGamePhase.PLAY_CARD,
                         host=c, trigger=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if (tp.tp == ETimePoint.DESTROYING) and (tp.args[1] is self.host) and (tp not in self.reacted):
            return True
        return False

    def cost(self, tp):
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
        # 输出
        super().execute()
        # 摧毁无效
        self.reacted.pop().args[-1] = 0
        self.host.remove_effect(self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
