# 笃诚信徒
from utils.constants import EEffectDesc, ETimePoint, ELocation, EEmployeeType, ECardType, ECardRank
from utils.common_effects import EffLazyTriggerCostMixin
from core.game import GameCard


class E1(EffLazyTriggerCostMixin):
    """
    摧毁卡。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DESTROY, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEF_CALC:
            op = self.game.players[self.game.get_player(self.host).sp]
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) &\
                    (tp not in self.reacted) & (tp.args[0] is op.leader) & (tp.args[1] < 3000):
                return True
        return False

    def execute(self):
        self.game.destroy(self.host, self.host, self)
        p = self.game.get_player(self.host)
        op = self.game.players[p.sp]
        for pos in range(0, 3):
            if op.on_field[pos] is None:
                c = GameCard(self.game, ELocation.UNKNOWN + 2 - op.sp)
                c.create('拉面神的海盗使者', ECardType.EMPLOYEE, EEmployeeType.COMMON, ECardRank.TRUMP,
                         2000, 2000)
                self.game.special_summon(p, op, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
