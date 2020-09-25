# 嫉妒者
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffLazyTriggerCostMixin


class E1(EffLazyTriggerCostMixin):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) &\
                    ((tp.args[0].location & (1 + self.game.get_player(self.host).sp)) > 0) &\
                    ('知名人士' in tp.args[0].series):
                return True
        return False

    def execute(self):
        self.game.deal_damage(self.host, self.game.get_player(self.host).leader, 3000, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
