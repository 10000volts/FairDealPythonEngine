# 街头霸王
from core.game import GameCard
from utils.common_effects import EffSummon, EffAgile
from utils.constants import EEffectDesc, ELocation


class E1(EffSummon):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2HAND, host=host)

    def execute(self):
        p = self.game.get_player(self.host)
        c = GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '66263624', is_token=True)
        self.game.send2hand(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(EffAgile(c))
