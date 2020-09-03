# 蓝图设计者
from utils.common_effects import EffLazyTriggerCostMixin
from utils.constants import EEffectDesc, ETimePoint, ELocation


class E1(EffLazyTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.VICTORY)

    def condition(self, tp):
        if tp.tp == ETimePoint.ASK4EFFECT:
            if self.host.location & ELocation.HAND:
                p = self.game.get_player(self.host)
                if (len(p.hand) == 1) & (len(p.deck) == 0):
                    for c in p.on_field:
                        if c is not None:
                            return False
                    self.game.show_card(p, self.host.vid, self)
                    return True
        return False

    def execute(self):
        self.game.win_reason = 1
        self.game.winner = self.game.get_player(self.host)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
