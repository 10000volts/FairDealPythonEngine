# 金融风暴
from models.effect import Effect
from utils.constants import EEffectDesc, ETimePoint, ECardType, ELocation
from core.game import TimePoint


class E1(Effect):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=host)

    def condition(self, tp):
        if tp is None:
            for c in self.game.get_player(self.host).hand:
                tp = TimePoint(ETimePoint.IN_EXILED, self, [c, 1])
                self.game.enter_time_point(tp)
                if tp.args[-1]:
                    return True
        return False

    def cost(self, tp):
        # 选择1手牌移除
        p = self.game.get_player(self.host)

        def check(c):
            return c.location == ELocation.HAND + 2 - p.sp
        return self.game.req4exile(check, p, p, 1, self) is not None

    def execute(self):
        for p in self.game.players:
            for c in p.on_field:
                if c is not None and c.type == ECardType.EMPLOYEE:
                    c.ATK.plus(0.5, False, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
