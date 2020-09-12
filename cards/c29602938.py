# 金属乐迷
from utils.constants import EEffectDesc, ETimePoint
from utils.common_effects import EffTriggerCostMixin


class E1(EffTriggerCostMixin):
    """
    击溃对方雇员时拿走。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2HAND, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            return (tp.args[0] is self.host) & (tp.sender is None) & \
                   (self.game.get_player(tp.args[1]) is not self.game.get_player(self.host))
        return False

    def execute(self):
        # todo: 应该不会在效果发动时转移控制权吧？
        p = self.game.get_player(self.host)
        self.game.send2hand(p, p, self.reacted.pop().args[1], self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
