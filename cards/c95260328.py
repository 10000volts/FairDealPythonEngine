# 密灵西
from models.effect import Effect
from utils.constants import EEffectDesc, EGamePhase, ETimePoint, ELocation


class E1(Effect):
    """
    附加值变成+1000。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ADDV_CHANGE, act_phase=EGamePhase.EXTRA_DATA,
                         host=c, trigger=True, secret=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if not super().condition(tp):
            return False

        if tp.tp == ETimePoint.PH_EXTRA_DATA_END and tp not in self.reacted:
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
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return (self.game.get_player(c) is self.game.get_player(self.host)) & \
                   ((c.location & ELocation.HAND) > 0)

        super().execute()

        tgt = self.game.choose_target(check, self, False, False)
        if tgt is not None:
            tgt.ATK.add_val = 1000


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e1 = E1(c)
    c.register_effect(e1)
