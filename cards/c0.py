# 默认领袖
from models.effect import Effect
from utils.constants import EEffectDesc, EGamePhase, ETimePoint


class E2(Effect):
    """
    攻击力复原。
    """
    def __init__(self, c, op, v):
        super().__init__(EEffectDesc.PROPERTY_CHANGE, EGamePhase.PLAY_CARD,
                         c, True, True)
        self.scr_arg = [op, v]

    def condition(self):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if not super().condition():
            return False

        for tp in self.game.tp_stack[::-1]:
            if tp.tp == ETimePoint.TURN_END and tp not in self.reacted:
                return True
        return False

    def cost(self):
        """
        支付cost，触发式效果需要在此添加连锁到的时点(且必须在进入新的时点前)。
        :return:
        """
        for tp in self.game.tp_stack[::-1]:
            if tp.tp == ETimePoint.TURN_END and tp not in self.reacted:
                self.reacted.append(tp)
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        self.host.ATK.remove(*self.scr_arg)
        self.host.remove_effect(self)


class E1(Effect):
    """
    自己的雇员入场后ATK+500。
    """
    def __init__(self, c):
        super().__init__(EEffectDesc.PROPERTY_CHANGE, EGamePhase.PLAY_CARD,
                         c, True, True)

    def condition(self):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if not super().condition():
            return False

        sd = self.game.get_player(self.host)
        for tp in self.game.tp_stack[::-1]:
            if tp.tp == ETimePoint.SUCC_SUMMON and self.host.game.get_player(tp.args[0]) is sd\
                    and tp not in self.reacted:
                return True
        return False

    def cost(self):
        """
        支付cost，触发式效果需要在此添加连锁到的时点(且必须在进入新的时点前)。
        :return:
        """
        sd = self.game.get_player(self.host)
        for tp in self.game.tp_stack[::-1]:
            if tp.tp == ETimePoint.SUCC_SUMMON and self.host.game.get_player(tp.args[0]) is sd\
                    and tp not in self.reacted:
                self.reacted.append(tp)
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()
        tp = self.reacted[-1]
        c = tp.args[0]
        op, v = c.ATK.gain(500)
        c.register_effect(E2(c, op, v), True)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e1 = E1(c)
    c.register_effect(e1)
