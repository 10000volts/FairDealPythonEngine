# 复古左轮
from utils.common_effects import EffSingleStgE1Mixin, EffSingleStgE2, EffSingleStgE3Mixin,\
    EffTriggerCostMixin
from utils.constants import EEffectDesc, ELocation, ECardType, ETimePoint


class E4(EffTriggerCostMixin):
    """
    击溃对方雇员时给予伤害。
    """
    def __init__(self, host, c):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host, trigger=True, force=True,
                         scr_arg=c)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            return (tp.args[0] is self.scr_arg) & (tp.sender is None) & \
                   (self.game.get_player(tp.args[1]) is not self.game.get_player(self.host))
        return False

    def execute(self):
        self.game.deal_damage(self.host, self.game.get_player(self.reacted.pop().args[1]).leader,
                              1000, self)


class E3(EffSingleStgE3Mixin):
    def __init__(self, host, c, op, v, ef):
        super().__init__(host=host, scr_arg=[c, op, v, ef])

    def execute(self):
        self.scr_arg[0].ATK.remove(self.scr_arg[1], self.scr_arg[2])
        if self.scr_arg[3] is not None:
            self.scr_arg[0].remove_effect(self.scr_arg[3])
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
        tgt = self.game.choose_target(p, p, check, self, True)
        if tgt is not None:
            op, v = tgt.ATK.gain(self.host.ATK.value, False, self)
            e5 = E4(self.host, tgt)
            tgt.register_effect(e5, True)
            e3 = E3(self.host, tgt, op, v, e5)
            self.host.register_effect(e3)
            self.host.register_effect(EffSingleStgE2(self.host, [tgt]))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
