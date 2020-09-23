# 战争骨骼
from utils.constants import EEffectDesc, ETimePoint
from utils.common_effects import EffTriggerCostMixin


class E1(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=host, trigger=True, force=True, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            return tp.args[0] is self.host
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        self.host.ATK.gain_x(self.x, False, self)

    def x(self, c):
        p = self.game.get_player(c)
        op = self.game.players[p.sp]
        if op.leader.DEF.value > p.leader.DEF.value:
            return op.leader.DEF.value - p.leader.DEF.value


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
