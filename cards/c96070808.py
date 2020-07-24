# 假博士
from utils.common_effects import EffTriggerCostMixin
from utils.constants import EEffectDesc, EGamePhase, ETimePoint


class E1(EffTriggerCostMixin):
    """
    造成伤害。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, act_phase=EGamePhase.TAKE_CARD,
                         host=host, trigger=True, force=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.CARD_TOOK and tp.args is self.host\
                and tp not in self.reacted:
            return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 给予取走者1000伤害。
        self.game.deal_damage(self.host, self.game.get_player(self.host).leader,
                              1000, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
