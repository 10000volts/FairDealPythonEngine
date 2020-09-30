# 人言可畏
from utils.common_effects import EffSingleStgE1Mixin
from utils.constants import EEffectDesc, ECardType, ELocation


class E1(EffSingleStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host)

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
        tgt = self.game.choose_target_from_func(p, p, check, self)
        if tgt is not None:
            op = self.game.players[p.sp]
            v = self.host.ATK.value
            tgt.ATK.gain(v, False, self)
            self.game.deal_damage(self.host, op.leader, v, self)
            self.game.heal(self.host, p.leader, v, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
