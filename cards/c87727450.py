# 金融风暴
from models.effect import Effect
from utils.constants import EEffectDesc, ETimePoint, ECardType
from core.game import TimePoint


class E1(Effect):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=host, scr_arg=0)

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
        if tp not in self.reacted:
            self.reacted.append(tp)
            p = self.game.get_player(self.host)

            def check(c):
                return c in p.hand
            return self.game.req4exile(check, self.game.get_player(self.host), 1, self)
        return False

    def execute(self):
        for p in self.game.players:
            for c in p.on_field:
                if c is not None and c.type == ECardType.EMPLOYEE:
                    c.ATK.plus(0.5)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
