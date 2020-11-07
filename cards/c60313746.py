# 恩怨
from models.effect import Effect
from utils.constants import EEffectDesc, ETimePoint, ECardType, ELocation
from core.game import TimePoint
from utils.common_effects import EffTriggerCostMixin, EffUntil


class E4(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.DESTROY, trigger=True, force=True, no_reset=True)

    def condition(self, tp):
        return tp.tp == ETimePoint.TURN_END

    def execute(self):
        for c in self.game.get_player(self.host).on_field:
            if c is not None and c.type == ECardType.EMPLOYEE:
                self.game.destroy(self.host, c, self)
        self.host.remove_effect(self)


class E2(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.ATK_LOSE, trigger=True, force=True, no_reset=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYING_SURE:
            return (self.game.get_player(tp.args[1]) is self.game.get_player(self.host)) & \
                   (tp.sender is None) & (tp.args[1].type == ECardType.EMPLOYEE)
        return False

    def execute(self):
        tp = self.reacted.pop()
        if tp.args[0].location & ELocation.ON_FIELD:
            tp.args[0].ATK.gain(-tp.args[1].ATK.value, False, self)


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
        self.reacted.append(tp)
        p = self.game.get_player(self.host)

        def check(c):
            return c in p.hand
        return self.game.req4exile(check, self.game.get_player(self.host), 1, self) is not None

    def execute(self):
        e2 = E2(self.host)
        self.host.register_effect(e2)
        self.host.register_effect(EffUntil(self.host, e2, lambda tp: tp.tp == ETimePoint.TURN_END))
        self.host.register_effect(E4(self.host))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
