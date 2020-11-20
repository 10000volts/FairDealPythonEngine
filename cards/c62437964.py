# 异色瞳的老黑猫
from utils.common_effects import EffTriggerCostMixin
from utils.constants import EEffectDesc, ETimePoint, ELocation
from core.game import GameCard


class E1(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.SEND2HAND, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            return (tp.sender is None) & (tp.args[1] is self.host)
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)
        c = GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '17493914', is_token=True)
        c.ATK.change_adv(self.host.ATK.add_val)
        self.game.send2hand(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
