# 伪造推荐信
from core.game import TimePoint, GameCard
from utils.constants import EEffectDesc, EEmployeeType, ETimePoint, ELocation, ECardType, ECardRank
from utils.common_effects import EffCostMixin


class E1(EffCostMixin):
    """
    特召。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=c)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp is None:
            p = self.game.get_player(self.host)
            op = self.game.players[p.sp]
            for c in p.hand:
                if (c.type == ECardType.EMPLOYEE) & (c.rank == ECardRank.COMMON):
                    for posture in range(0, 2):
                        for pos in range(0, 3):
                            if op.on_field[pos] is None:
                                tp = TimePoint(ETimePoint.TRY_SUMMON, self, [c, op, pos, posture, 1])
                                self.game.enter_time_point(tp)
                                if tp.args[-1]:
                                    for pos2 in range(0, 3):
                                        if op.on_field[pos2] is None:
                                            return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 选手牌1雇员进入对方场地
        p = self.game.get_player(self.host)
        op = self.game.players[p.sp]

        def check(c):
            f = False
            if (c.location & (2 - p.sp + ELocation.HAND)) & (c.type == ECardType.EMPLOYEE):
                for posture in range(0, 2):
                    for pos in range(0, 3):
                        if op.on_field[pos] is None:
                            tp = TimePoint(ETimePoint.TRY_SUMMON, self, [c, op, pos, posture, 1])
                            self.game.enter_time_point(tp)
                            f |= tp.args[-1]
                if not f:
                    return False
                for posture in range(0, 2):
                    for pos in range(0, 3):
                        if p.on_field[pos] is None:
                            tp = TimePoint(ETimePoint.TRY_SUMMON, self, [c, p, pos, posture, 1])
                            self.game.enter_time_point(tp)
                            if tp.args[-1]:
                                return True
                return False
        tgt = self.game.choose_target(p, p, check, self, False, False)
        if tgt is not None:
            atk = tgt.ATK.value
            self.game.special_summon(p, op, tgt, self)
            c = GameCard(self.game)
            c.create('随行者', ECardType.EMPLOYEE, EEmployeeType.COMMON, ECardRank.COMMON,
                     atk, 0)
            self.game.special_summon(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
