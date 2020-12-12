# 紧逼
from utils.common_effects import EffSingleStgE1Mixin, EffSingleStgE2, EffSingleStgE3Mixin,\
    EffLazyTriggerCostMixin, EffPierce
from utils.constants import EEffectDesc, ELocation, ECardType, ETimePoint


class E3(EffSingleStgE3Mixin):
    def __init__(self, host, c, op, v):
        super().__init__(host=host, scr_arg=[c, op, v, None])

    def execute(self):
        self.scr_arg[0].remove_buff(self.scr_arg[1], self.scr_arg[2])
        if self.scr_arg[3] is not None:
            self.scr_arg[0].remove_effect(self.scr_arg[3])
        self.host.remove_effect(self)


class E4(EffLazyTriggerCostMixin):
    def __init__(self, host, c, e3):
        super().__init__(host=host, desc=EEffectDesc.REGISTER_EFFECT, trigger=True, force=True,
                         scr_arg=[c, e3])

    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_BEGIN:
            if self.game.turn_player == self.game.get_player(self.host):
                return True
        return False

    def execute(self):
        e5 = EffPierce(self.scr_arg[0], 5000)
        f = True
        for ef in self.scr_arg[0].effects:
            if ef.ef_id == EEffectDesc.PIERCE:
                f = False
        if f:
            self.scr_arg[0].register_effect(e5, True)
            self.scr_arg[1].scr_arg[3] = e5
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
            eff = 1000 if self.host.ATK.value > 1000 else self.host.ATK.value
            op, v = tgt.ATK.gain(eff, False, self)
            e3 = E3(self.host, tgt, op, v)
            self.host.register_effect(e3)
            e4 = E4(self.host, tgt, e3)
            self.host.register_effect(e4)
            self.host.register_effect(EffSingleStgE2(self.host, [tgt]))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
