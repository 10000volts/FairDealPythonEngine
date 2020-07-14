from models.effect import Effect
from utils.constants import EEffectDesc, EGamePhase, ETimePoint
from utils.common import adj_pos


class EffInvestigator(Effect):
    """
    调查筹码的效果。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.INVESTIGATE, act_phase=EGamePhase.PUT_CARD,
                         host=host, trigger=True, force_exec=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if not super().condition(tp):
            return False

        if (tp.tp == ETimePoint.CARD_PUT) and (tp.args[2] is self.host) \
                and (tp not in self.reacted):
            return True
        return False

    def cost(self, tp):
        """
        支付cost，触发式效果需要在此添加连锁到的时点(且必须在进入新的时点前)。
        :return:
        """
        if (tp.tp == ETimePoint.CARD_PUT) and (tp.args[2] is self.host) \
                and (tp not in self.reacted):
            self.reacted.append(tp)
            return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        g = self.game
        tp = self.reacted[-1]
        x = tp.args[0]
        y = tp.args[1]
        cs = adj_pos(x, y, g.scale)
        # 展示其中的对方卡
        sd = self.game.get_player(self.host)
        for c in cs:
            if g.chessboard[c] is not None:
                if (g.chessboard[c].location - sd.sp) % 2:
                    g.show_card(sd, g.chessboard[c].vid, self)
        self.host.remove_effect(self)


class CommonStrategyEffect(Effect):
    """
    常规策略的缺省效果。
    """
    def __init__(self, desc, c):
        super().__init__(desc=desc, act_phase=EGamePhase.PLAY_CARD, host=c)

    def condition(self, tp):
        return True
