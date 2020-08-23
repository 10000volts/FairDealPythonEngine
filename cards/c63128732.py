# 吉祥物
from utils.constants import EEffectDesc, ETimePoint, ECardType, ELocation
from utils.common_effects import EffSummon, EffLazyTriggerCostMixin, EffUntil


class E4(EffLazyTriggerCostMixin):
    """
    不能改变姿态。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.FORBIDDEN, host=host, trigger=True, force=True, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TRY_CHANGE_POSTURE:
            if (tp.args[0] is self.host) & (tp not in self.reacted):
                return True
        return False

    def execute(self):
        self.reacted.pop().args[-1] = 0


class E3(EffLazyTriggerCostMixin):
    """
    返场。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYING:
            p = self.game.get_player(self.host)
            return (tp.sender is None) & ((tp.args[1].location & (2 - p.sp)) > 0) & \
                   (tp.args[1].ATK.value == self.host.ATK.value) & \
                   (tp.args[1] is not self.host) & ((self.host.location & ELocation.GRAVE) > 0) & \
                   (tp not in self.reacted)
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        self.game.special_summon(p, p, self.host, self, 1)
        e4 = E4(self.host)
        self.host.register_effect(e4)
        self.host.register_effect(EffUntil(self.host, e4, lambda tp: ((tp.tp == ETimePoint.TURN_BEGIN) &
                                                                      (self.game.turn_player is not p))))


class E2(EffLazyTriggerCostMixin):
    """
    攻击力变化。
    """
    def __init__(self, host, tp):
        super().__init__(desc=EEffectDesc.ATK_CHANGE, host=host, trigger=True, force=True,
                         no_reset=True, scr_arg=tp)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            p = self.game.get_player(self.host)
            return (tp.args[0] in p.on_field) & (tp.args[0].type == ECardType.EMPLOYEE) & \
                (tp.args[0].ATK.value <= 1000) & (tp.args[0].cover == 0) & (tp not in self.reacted) & \
                   (tp is not self.scr_arg)
        return False

    def execute(self):
        em = self.reacted.pop().args[0]
        em.ATK.become(3000 - em.ATK.value)
        self.host.remove_effect(self)


class E1(EffSummon):
    """
    附加效果。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.REGISTER_EFFECT, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 注册效果
        self.host.register_effect(E2(self.host, self.reacted.pop()), True)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E3(c))
