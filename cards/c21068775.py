# 赛博酒保
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffLazyTriggerCostMixin, EffSummon


class E2(EffLazyTriggerCostMixin):
    def __init__(self, c, p):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=c, trigger=True, force=True, no_reset=True,
                         scr_arg=[p, 0])

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if (not self.host.cover) & ((tp.args[0].location & (1 + self.scr_arg[0].sp)) > 0):
                return True
        return False

    def execute(self):
        if self.scr_arg[1] == 0:
            self.reacted.pop().args[0].ATK.gain(-100, False, self)
        elif self.scr_arg[1] == 1:
            self.reacted.pop().args[0].ATK.gain(-300, False, self)
        elif self.scr_arg[1] == 2:
            self.reacted.pop().args[0].ATK.gain(-700, False, self)
            self.host.remove_effect(self)
        self.scr_arg[1] += 1


class E1(EffSummon):
    """
    攻击力上升。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.REGISTER_EFFECT, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 我方场上全部雇员ATK+500
        self.host.register_effect(E2(self.host, self.game.get_player(self.host)))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
