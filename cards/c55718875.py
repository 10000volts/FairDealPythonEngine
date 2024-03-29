# 对症下药
from utils.common_effects import EffSingleStgE1Mixin
from utils.constants import EEffectDesc, ECardType, ELocation, EChoice


class E1(EffSingleStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.PROPERTY_CHANGE, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        r = p.req4option([EChoice.CHANGE_ATK, EChoice.CHANGE_DEF])
        if r == EChoice.CHANGE_ATK:
            tgt = self.game.choose_target_from_func(p, p, check, self)
            if tgt is not None:
                tgt.ATK.gain(-self.host.ATK.value, False, self)
        else:
            tgt = self.game.choose_target_from_func(p, p, check, self)
            if tgt is not None:
                tgt.DEF.gain(-self.host.ATK.value, False, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
