from models.effect import Effect
from utils.constants import EEffectDesc, EGamePhase, ETimePoint
from utils.common import adj_pos


class EffInvestigator(Effect):
    """
    调查筹码的效果。
    """
    def __init__(self, owner, host):
        super().__init__(desc=EEffectDesc.INVESTIGATE, act_phase=EGamePhase.PUT_CARD,
                         owner=owner, host=host, trigger=True, force_exec=True)

    def condition(self):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if not super().condition():
            return False

        for tp in self.game.tp_stack:
            if tp.tp == ETimePoint.CARD_PUT and tp.args[2] == self.host\
                    and tp not in self.reacted:
                return True
        return False

    def cost(self):
        """
        支付cost，触发式效果需要在此添加连锁到的时点。
        :return:
        """
        for tp in self.game.tp_stack:
            if tp.tp == ETimePoint.CARD_PUT and tp.args[2] == self.host \
                    and tp not in self.reacted:
                self.reacted.append(tp)
                return True

    def execute(self):
        """
        执行效果。
        :return:
        """
        g = self.game
        tp = self.reacted[-1]
        x = tp.args[0]
        y = tp.args[1]
        cs = adj_pos(x, y, g.scale)
        # 展示其中的对方卡
        for c in cs:
            if g.chessboard[c] is not None:
                if (g.chessboard[c].location - self.owner.sp) % 2:
                    g.show_card(self.owner, g.chessboard[c].vid, self)
        self.host.remove_effect(self)
