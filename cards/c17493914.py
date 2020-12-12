# 凝视
from utils.common_effects import EffSingleStgE1Mixin, EffNextTurnMixin
from utils.constants import EEffectDesc, ECardType, ELocation


class E2(EffNextTurnMixin):
    """
    回合开始时回复攻击力。
    """
    def __init__(self, host, c, op, v):
        super().__init__(desc=EEffectDesc.EFFECT_END,
                         host=host, trigger=True, force=True, scr_arg=[c, op, v], no_reset=True, passive=True)

    def execute(self):
        self.scr_arg[0].remove_buff(self.scr_arg[1], self.scr_arg[2])
        self.host.remove_effect(self)


class E1(EffSingleStgE1Mixin):
    """
    ATK+EFF(至少500)。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_CHANGE, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, check, self)
        if tgt is not None:
            op, v = tgt.ATK.gain(self.host.ATK.add_val, False, self)
            self.host.register_effect(E2(self.host, tgt, op, v))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
