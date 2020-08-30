# 定时炸弹
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffLazyTriggerCostMixin


class E1(EffLazyTriggerCostMixin):
    """
    摧毁卡。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DESTROY, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) &\
                    (tp not in self.reacted) & (tp.args[0] is not self.host) & (tp.args[0].ATK.value == 0):
                return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        self.game.destroy(self.host, self.host, self)
        if len(p.on_field) > 0:
            tgt = self.game.choose_target(p, self.game.players[p.sp],
                                          lambda c: c.location == ELocation.ON_FIELD + 2 - p.sp, self, False)
            self.game.destroy(self.host, tgt, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
