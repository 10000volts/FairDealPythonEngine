# 招聘
from core.game import GameCard
from utils.constants import EEffectDesc, EEmployeeType, ECardType, ECardRank
from utils.common_effects import EffTurnCostMixin


class E1(EffTurnCostMixin):
    """
    特召。
    """

    def __init__(self, c):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=c, ef_id='735293260')

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        p = self.game.get_player(self.host)
        if (tp is None) & (self.ef_id not in p.ef_limiter):
            for pos in range(0, 3):
                if p.on_field[pos] is None:
                    return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)
        c = GameCard(self.game)
        c.create('应聘者', ECardType.EMPLOYEE, EEmployeeType.COMMON, ECardRank.COMMON,
                 self.host.ATK.value, 0)
        self.game.special_summon(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
