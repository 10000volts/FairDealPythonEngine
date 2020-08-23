# 过河拆桥
from utils.constants import EEffectDesc, ETimePoint, ECardType
from core.game import TimePoint
from utils.common_effects import EffTriggerCostMixin


class E1(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host)

    def condition(self, tp):
        if tp is None:
            p = self.game.get_player(self.host)
            op = self.game.players[p.sp]
            for c1 in p.on_field:
                if c1 is not None and c1.type == ECardType.EMPLOYEE:
                    tp = TimePoint(ETimePoint.TRY_CHOOSE_TARGET, self, [c1, 1])
                    self.game.enter_time_point(tp)
                    if tp.args[-1]:
                        for c in op.on_field:
                            if c is not None and c.type == ECardType.STRATEGY:
                                tp = TimePoint(ETimePoint.TRY_CHOOSE_TARGET, self, [c, 1])
                                self.game.enter_time_point(tp)
                                if tp.args[-1]:
                                    return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        op = self.game.players[p.sp]
        tgt1 = self.game.choose_target(p, p, lambda c: (((c in p.on_field) &
                                                      (c.type == ECardType.EMPLOYEE))), self, True)
        tgt2 = self.game.choose_target(p, p, lambda c: ((c in op.on_field) &
                                                      (c.type == ECardType.STRATEGY)), self, True)
        self.game.destroy(self.host, tgt1, self)
        self.game.destroy(self.host, tgt2, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
