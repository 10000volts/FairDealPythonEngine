# 鼓舞
from utils.common_effects import EffSingleStgE1Mixin, EffSingleStgE2, EffSingleStgE3Mixin
from utils.constants import EEffectDesc, ELocation, ECardType


class E3(EffSingleStgE3Mixin):
    def __init__(self, host, c, op, v):
        super().__init__(host=host, scr_arg=[c, op, v])

    def execute(self):
        self.scr_arg[0].remove_buff(self.scr_arg[1], self.scr_arg[2])
        self.scr_arg[0].ATK.update()
        self.host.remove_effect(self)


class E1(EffSingleStgE1Mixin):
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
        # 选择1雇员ATK+EFF
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, check, self, True)
        if tgt is not None:
            op, v = tgt.ATK.gain(1000 if self.host.ATK.value > 1000 else self.host.ATK.value,
                                 False, self)
            self.host.register_effect(E3(self.host, tgt, op, v))
            self.host.register_effect(EffSingleStgE2(self.host, [tgt]))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
