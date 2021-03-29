# 彩票学家
from models.effect import Effect
from utils.common_effects import EffSummon
from utils.constants import EEffectDesc, ETimePoint, ELocation


class E1(Effect):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.HEAL, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TURN_BEGIN:
            p = self.game.get_player(self.host)
            return (self.host.location == ELocation.HAND + 2 - p.sp) & (self.ef_id not in p.ef_limiter) & \
                   (self.game.turn_player is p)
        return False

    def cost(self, tp):
        self.reacted.append(tp)
        if self.condition(tp):
            self.game.show_card(self.game.get_player(self.host), self.host.vid, self)
            return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        p.leader.effects[0].scr_arg += self.host.ATK.value / 2


class E2(EffSummon):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.VICTORY, host=host)

    def condition(self, tp):
        if super().condition(tp):
            p = self.game.get_player(self.host)
            return p.leader.DEF.value == 16000
        return False

    def execute(self):
        self.game.win_reason = 1
        self.game.winner = self.game.get_player(self.host)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
