# 和声姐妹花 布伦娜
from core.game import GameCard
from utils.common_effects import EffLazyTriggerCostMixin
from utils.constants import EEffectDesc, ETimePoint, ELocation


class E1(EffLazyTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2DECK, host=host, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            return tp.args[1] is self.host
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        c = GameCard(self.game, ELocation.UNKNOWN + 2 - p.sp, '9612125', is_token=True)
        self.game.send2deck(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
