# 转移视线
from utils.common_effects import EffSingleStgE1Mixin, EffLazyTriggerCostMixin
from utils.constants import EEffectDesc, ECardType, ELocation, ETimePoint


class E3(EffLazyTriggerCostMixin):
    """
    满足条件时删除效果。
    """
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.REMOVE_EFFECT,
                         host=host, trigger=True, force=True, scr_arg=[ef, 0])

    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_BEGIN:
            return self.game.turn_player is self.game.get_player(self.host)
        return False

    def execute(self):
        if self.scr_arg[1] < 2:
            self.scr_arg[1] += 1
            return
        self.host.remove_effect(self.scr_arg[0])
        self.host.remove_effect(self)


class E2(EffLazyTriggerCostMixin):
    """
    不能攻击
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.INVALID, host=host, trigger=True, force=True, passive=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.TRY_ATTACK:
            # 攻击者是自己
            return tp.args[0] is self.host
        return False

    def execute(self):
        # 无效
        self.reacted.pop().args[-1] = 0


class E1(EffSingleStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.FORBIDDEN, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self)
        if tgt is not None:
            e2 = E2(tgt)
            tgt.register_effect(e2, True)
            tgt.register_effect(E3(tgt, e2))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
