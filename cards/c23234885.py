# 超额执行
from utils.common_effects import EffSingleStgE1Mixin, EffAttackLimit, EffUntil
from utils.constants import EEffectDesc, ECardType, ELocation, ETimePoint


class E2(EffAttackLimit):
    """
    不能直接攻击
    """
    def __init__(self, c):
        super().__init__(host=c, can_invalid=False)


class E1(EffSingleStgE1Mixin):
    """
    指定的目标本回合可额外攻击2次
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.EXTRA_CHANCE, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()

        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        # 选择1雇员本回合可最多3次向雇员攻击
        tgt = self.game.choose_target(check, self)
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
