# 和声姐妹花 布伦娜
from core.game import GameCard, TimePoint
from utils.common_effects import EffLazyTriggerCostMixin
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType


class E1(EffLazyTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2DECK, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            if tp.args[1] is self.host:
                for c in self.game.get_player(self.host).grave:
                    if (c.type == ECardType.EMPLOYEE) & ('和声姐妹花' not in c.series):
                        tp = TimePoint(ETimePoint.IN_EXILED, self, [c, 1])
                        self.game.enter_time_point(tp)
                        if tp.args[-1]:
                            return True
        return False

    def cost(self, tp):
        # 选择1牌移除
        self.reacted.append(tp)
        p = self.game.get_player(self.host)

        def check(c):
            return (c.location == ELocation.GRAVE + 2 - p.sp) & ('和声姐妹花' not in c.series) & \
                   (c.type == ECardType.EMPLOYEE)
        return self.game.req4exile(check, p, p, 1, self) is not None

    def execute(self):
        p = self.game.get_player(self.host)
        c = GameCard(self.game, ELocation.UNKNOWN + 2 - p.sp, '9612125', is_token=True)
        self.game.send2deck_above(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
