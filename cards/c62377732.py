# 催眠
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin, EffCommonStrategy
from core.game import GameCard


class E1(EffCommonStrategy):
    """
    回复生命。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=c, passive=True)

    def execute(self):
        pass


class E2(EffTriggerCostMixin):
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_ENDING:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover)\
                    & (self.game.turn_player is self.game.get_player(self.host)):
                return True
        return False

    def execute(self):
        for p in self.game.players:
            c = p.on_field[self.host.inf_pos - 3]
            if c is not None:
                c.ATK.gain(-self.host.ATK.value, False, self)


class E3(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2HAND, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.DESTROYED:
            if tp.args[1] is self.host:
                return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        c = GameCard(self.game, ELocation.UNKNOWN + 2 - p.sp, '62377732', is_token=True)
        self.game.send2hand(p, p, c, self)
        c = GameCard(self.game, ELocation.UNKNOWN + 2 - p.sp, '62377732', is_token=True)
        self.game.send2hand(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
    c.register_effect(E3(c))
