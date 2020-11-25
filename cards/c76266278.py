# 删库跑路前科人员
from utils.common_effects import EffLazyTriggerCostMixin
from utils.constants import EEffectDesc, ETimePoint


class E1(EffLazyTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host, trigger=True, force=True, ef_id='762662780')

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYING_SURE:
            return (tp.args[1] is self.host) & (self.ef_id not in self.game.get_player(self.host).ef_g_limiter)
        return False

    def execute(self):
        self.game.deal_damage(self.host, self.game.get_player(self.host).leader, 2000, self)
        self.game.get_player(self.host).ef_g_limiter[self.ef_id] = 1


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
