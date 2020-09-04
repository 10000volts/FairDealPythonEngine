# 蓝图设计者
from utils.common_effects import EffSummon
from utils.constants import EEffectDesc


class E1(EffSummon):
    """
    对对方玩家造成500伤害。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host)

    def condition(self, tp):
        if super().condition(tp):
            p = self.game.get_player(self.host)
            if (len(p.hand) == 0) & (len(p.deck) == 0):
                for c in p.on_field:
                    if c is not None and c is not self.host:
                        return False
                return True
        return False

    def execute(self):
        p = self.game.players[self.game.get_player(self.host).sp]
        self.game.deal_damage(self.host, p.leader, self.host.ATK.value * 2, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
