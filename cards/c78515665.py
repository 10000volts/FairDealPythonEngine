# 笃诚信徒
from utils.constants import EEffectDesc, ETimePoint, ELocation, EEmployeeType, ECardType, ECardRank
from utils.common_effects import EffTriggerCostMixin
from core.game import GameCard, TimePoint


class E1(EffTriggerCostMixin):
    """
    摧毁卡。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DESTROY, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEF_CALC:
            op = self.game.players[self.game.get_player(self.host).sp]
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) &\
                    (tp.args[0] is op.leader) & (tp.args[1] < 3000):
                for posture in range(0, 2):
                    for pos in range(0, 3):
                        if op.on_field[pos] is None:
                            # todo: 偷了个懒
                            tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, op, pos, posture, 1])
                            self.game.enter_time_point(tp)
                            if tp.args[-1]:
                                return True
                return True
        return False

    def execute(self):
        self.game.destroy(self.host, self.host, self)
        op = self.game.players[self.game.get_player(self.host).sp]
        for pos in range(0, 3):
            if op.on_field[pos] is None:
                c = GameCard(self.game, ELocation.UNKNOWN + 2 - op.sp)
                c.create('拉面神的海盗使者', ECardType.EMPLOYEE, EEmployeeType.COMMON, ECardRank.TRUMP,
                         2000, 2000)
                self.game.special_summon(op, op, c, self)
                return


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
