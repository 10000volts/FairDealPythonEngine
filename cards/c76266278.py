# 删库跑路前科人员
from utils.common_effects import EffLazyTriggerCostMixin
from utils.constants import EEffectDesc, ETimePoint


class E1(EffLazyTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            return tp.args[1] is self.host
        return False

    def execute(self):
        self.game.deal_damage(self.host, self.game.get_player(self.host).leader, 2000, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
