# 幕后黑手
from models.effect import Effect
from core.game import GameCard, TimePoint
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType, EEmployeeType, ECardRank


class E1(Effect):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.SPECIAL_SUMMON)

    def condition(self, tp):
        if tp.tp == ETimePoint.ASK4EFFECT:
            p = self.game.get_player(self.host)
            if self.host.location == ELocation.HAND + 2 - p.sp:
                op = self.game.players[p.sp]
                for c in op.grave:
                    if (c.type == ECardType.STRATEGY) & (c.ATK.value == 0):
                        return True
        return False

    def cost(self, tp):
        if self.condition(tp):
            p = self.game.get_player(self.host)
            op = self.game.players[p.sp]

            def check(c):
                return (c.type == ECardType.STRATEGY) & (c.ATK.value == 0) & \
                       (c.location == ELocation.GRAVE + 2 - op.sp)
            self.game.show_card(p, self.host.vid, self)
            return self.game.ceremony(p, check, 0, ELocation.EXILED,
                                      '=', False)
        return False

    def execute(self):
        self.host.ATK.gain(1000, True, self)
        p = self.game.get_player(self.host)
        c = GameCard(self.game, ELocation.UNKNOWN + 2 - p.sp)
        c.create('幕后黑手的人偶', ECardType.EMPLOYEE, EEmployeeType.COMMON, ECardRank.TRUMP,
                 1000, 1000)

        for pos in range(0, 3):
            for posture in range(0, 2):
                if p.on_field[pos] is None:
                    tp = TimePoint(ETimePoint.TRY_SUMMON, self, [c, p, pos, posture, 1])
                    self.game.enter_time_point(tp)
                    if tp.args[-1]:
                        self.game.special_summon(p, p, c, self)
                        return


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
