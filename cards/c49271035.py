# 数据分析师
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, EErrorCode
from utils.common import adj_pos


class E2(Effect):
    """
    调查筹码。
    """
    def __init__(self, ef):
        super().__init__(desc=EEffectDesc.WEAK_INVESTIGATE, act_phase=EGamePhase.PUT_CARD,
                         host=ef.host, trigger=True, force=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.CARD_PUT and tp.args[2] is self.host\
                and tp not in self.reacted:
            return True
        return False

    def cost(self, tp):
        """
        支付cost，触发式效果需要在此添加连锁到的时点(且必须在进入新的时点前)。
        :return:
        """
        if self.condition(tp):
            self.reacted.append(tp)
            return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check_ind(_ind):
            if _ind not in range(0, chs_len):
                return EErrorCode.OVERSTEP
            return 0

        # 输出
        super().execute()
        g = self.game
        tp = self.reacted.pop()
        x = tp.args[0]
        y = tp.args[1]
        cs = adj_pos(x, y, g.scale)
        chs = list()
        # 剔除其中的无效卡
        sd = self.game.get_player(self.host)
        for c in cs:
            if g.chessboard[c] is not None:
                if (g.chessboard[c].location - sd.sp) % 2:
                    chs.append(g.chessboard[c].vid)
        chs_len = len(chs)
        if chs_len:
            ind = sd.free_input(check_ind, 'req_chs_tgt', [chs, 1])
            if ind is not None:
                g.show_card(sd, chs[ind], self)
        self.host.remove_effect(self)


class E1(Effect):
    """
    询问。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.BECOME_INVESTIGATE, act_phase=EGamePhase.EXTRA_DATA,
                         host=c, trigger=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.PH_EXTRA_DATA_END and tp not in self.reacted:
            p = self.game.get_player(self.host)
            tp2 = TimePoint(ETimePoint.TRY_HP_COST, self, [p, 1000, 1])
            self.game.enter_time_point(tp2)
            if tp2.args[-1] & (p.leader.DEF.value > tp2.args[1]):
                return True
        return False

    def cost(self, tp):
        """
        支付cost，触发式效果需要在此添加连锁到的时点(且必须在进入新的时点前)。
        :return:
        """
        sd = self.game.get_player(self.host)
        if self.condition(tp):
            self.reacted.append(tp)
            # 支付1000生命力
            f = sd.leader.hp_cost(1000, self)
            if next(f):
                next(f)
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()
        # 变成调查筹码后影响力值归零
        self.host.ATK.add_val = 0
        self.host.register_effect(E2(self), True)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
