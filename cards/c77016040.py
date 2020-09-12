# 高效雇员
from utils.constants import EEffectDesc, ETimePoint
from utils.common_effects import EffTriggerCostMixin
from core.game import TimePoint


class E1(EffTriggerCostMixin):
    """
    回合结束时回复。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.HEAL, host=host, trigger=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.TURN_END:
            p = self.game.get_player(self.host)
            # 是我方回合，在场
            if (self.game.turn_player is self.game.get_player(self.host)) & (self.host in p.on_field):
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)
        tp = TimePoint(ETimePoint.TRY_HEAL, self, [self.host, p.leader, self.host.ATK.value, 1])
        self.game.enter_time_point(tp)
        if tp.args[-1]:
            self.game.heal(self.host, p.leader, self.host.ATK.value, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
