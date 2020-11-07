# 蓝图设计者
from utils.common_effects import EffSummon, EffTriggerCostMixin
from utils.constants import EEffectDesc, ETimePoint


class E3(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.FORBIDDEN, host=host, trigger=True, force=True,
                         passive=True)

    def condition(self, tp):
        # 已经移除了所有其他效果，入场必定成功。
        if tp.tp == ETimePoint.SUCC_SUMMON:
            return tp.args[0] is self.host
        return False

    def execute(self):
        self.game.update_ef_list()
        self.host.remove_effect(self)


class E2(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.FORBIDDEN, host=host, trigger=True, force=True,
                         passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUMMONING:
            return tp.args[0] is self.host
        return False

    def execute(self):
        for ef in self.game.ef_listener:
            if ef.host is not self.host:
                self.game.ef_listener.remove(ef)
        self.host.register_effect(E3(self.host))


class E1(EffSummon):
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
        v = min(self.host.ATK.value * 2, 7000)
        self.game.deal_damage(self.host, p.leader, v, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
