# 超额执行
from utils.common_effects import EffSingleStgE1Mixin, EffUntil, EffLazyTriggerCostMixin
from utils.constants import EEffectDesc, ECardType, ELocation, ETimePoint


class E2(EffLazyTriggerCostMixin):
    """
    战斗伤害变成0
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DAMAGE_CHANGE, host=c, can_invalid=False, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEALING_DAMAGE:
            if (tp.sender is None) & (tp.args[0] == self.host):
                return True
        return False

    def execute(self):
        self.reacted.pop().args[2] = 0


class E1(EffSingleStgE1Mixin):
    """
    指定的目标本回合可额外攻击2次
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.EXTRA_CHANCE, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        # 选择1雇员本回合可最多3次向雇员攻击
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self)
        if tgt is not None:
            tgt.attack_times += 2
            e3 = E2(tgt)
            # 虽然这是超额执行的效果但无所谓
            tgt.register_effect(e3)
            tgt.register_effect(EffUntil(tgt, e3, lambda tp: tp.tp == ETimePoint.TURN_END))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
