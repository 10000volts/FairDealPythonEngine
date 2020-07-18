# 职业造谣者
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, ECardType, ELocation


class E1(Effect):
    """
    统计双方的出牌数。
    """
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host, trigger=True, force=True,
                         no_reset=True, scr_arg=[0, 0, ef])

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.IN_FIELD_END:
            # 离开手牌并到自己场上即为使用手牌。
            for t in self.game.tp_stack[::-1]:
                if t.tp == ETimePoint.OUT_HAND_END:
                    p = self.game.get_player(self.host)
                    if t.args[1] & (2 - p.sp):
                        return True
        return False

    def cost(self, tp):
        """
        支付cost，触发式效果需要在此添加连锁到的时点(且必须在进入新的时点前)。
        :return:
        """
        return True

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        super().execute()


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
