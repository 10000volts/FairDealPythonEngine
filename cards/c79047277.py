# 耍帅左轮
from utils.common_effects import EffSingleStgE1Mixin, EffSingleStgE2, EffSingleStgE3Mixin
from models.effect import Effect
from utils.constants import EEffectDesc, ELocation, ECardType, ETimePoint


class E4(Effect):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SET_CARD, host=host)

    def condition(self, tp):
        if tp.tp == ETimePoint.ASK4EFFECT:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (self.host.cover == 0):
                p = self.game.get_player(self.host)
                for c in p.hand:
                    if c.cid == '25930167':
                        return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        self.game.send2exiled(p, p, self.host, self)

        def check(c):
            return (c.location == ELocation.HAND + 2 - p.sp) & (c.cid == '25930167')
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
        if tgt is not None:
            self.game.set_strategy(p, p, tgt, self)


class E3(EffSingleStgE3Mixin):
    def __init__(self, host, c, op, v):
        super().__init__(host=host, scr_arg=[c, op, v])

    def execute(self):
        self.scr_arg[0].remove_buff(self.scr_arg[1], self.scr_arg[2])
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
        tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
        if tgt is not None:
            op, v = tgt.ATK.gain(self.host.ATK.value, False, self)
            e3 = E3(self.host, tgt, op, v)
            self.host.register_effect(e3)
            self.host.register_effect(EffSingleStgE2(self.host, [tgt]))
            for c in p.hand:
                if c.cid == '25930167':
                    c.ATK.change_adv(c.ATK.add_val + self.host.ATK.add_val, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E4(c))
