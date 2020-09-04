# 绩效奖金
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin, EffCommonStrategy


class E1(EffCommonStrategy):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=c, passive=True)

    def execute(self):
        pass


class E2(EffTriggerCostMixin):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEALT_DAMAGE:
            p = self.game.get_player(self.host)
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) & (tp not in self.reacted)\
                    & (tp.args[0].location == ELocation.ON_FIELD + 2 - p.sp) & (tp.sender is None) & \
                    (tp.args[1] is self.game.players[p.sp].leader):
                return True
        return False

    def execute(self):
        self.reacted.pop().args[0].ATK.gain(600 if self.host.ATK.value > 600 else self.host.ATK.value)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
