# 侦探爱好者
from utils.common_effects import EffPierce, EffTriggerCostMixin
from utils.constants import EEffectDesc, ETimePoint, ELocation


class E2(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEALT_DAMAGE:
            return (tp.args[0] is self.host) & ((self.host.location & ELocation.ON_FIELD) > 0) & \
                   (tp.args[1] is self.game.players[self.game.get_player(self.host).sp].leader) & \
                   (tp.args[2] > 0) & (tp not in self.reacted)
        return False

    def execute(self):
        self.host.ATK.gain(500)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(EffPierce(c))
    c.register_effect(E2(c))
