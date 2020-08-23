# 涨薪
from utils.common_effects import EffSingleStgE1Mixin, EffTurnEndMixin
from utils.constants import EEffectDesc, ECardType, ELocation


class E2(EffTurnEndMixin):
    """
    回合结束时回复攻击力。
    """
    def __init__(self, host, c, op, v):
        super().__init__(desc=EEffectDesc.EFFECT_END,
                         host=host, trigger=True, force=True, scr_arg=[c, op, v], no_reset=True, passive=True)

    def execute(self):
        self.scr_arg[0].ATK.remove(self.scr_arg[1], self.scr_arg[2])
        self.host.remove_effect(self)


class E1(EffSingleStgE1Mixin):
    """
    ATK+EFF(至少500)。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        # 选择1雇员ATK+EFF(至少500)直到回合结束
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self)
        if tgt is not None:
            op, v = tgt.ATK.gain(500 if self.host.ATK.value < 500 else self.host.ATK.value)
            self.host.register_effect(E2(self.host, tgt, op, v))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
