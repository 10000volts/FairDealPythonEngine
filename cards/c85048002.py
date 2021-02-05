# 甩锅
from utils.common_effects import EffCounterStgE2Mixin, EffCounterStgE1Mixin, EffTriggerCostMixin
from utils.constants import ETimePoint, EEffectDesc, ELocation


class E1(EffCounterStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.CHANGE_TARGET, host=host, scr_arg=[None], passive=True)

    def execute(self):
        # 无效攻击。
        self.scr_arg[0].args[1] = self.game.get_player(self.host).leader


class E2(EffCounterStgE2Mixin, EffTriggerCostMixin):
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.CHANGE_TARGET, host=host, scr_arg=[ef], trigger=True)

    def condition(self, tp):
        if self.host.turns:
            if tp.tp == ETimePoint.ATTACKING:
                if self.host.location & ELocation.ON_FIELD:
                    if self.host.cover:
                        p = self.game.get_player(self.host)
                        if tp.args[1].location == ELocation.ON_FIELD + 2 - p.sp:
                            return super().condition(self, tp)
        return False


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e1 = E1(c)
    c.register_effect(e1)
    c.register_effect(E2(c, e1))
