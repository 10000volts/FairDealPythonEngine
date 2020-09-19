# 信息大盗 杰拉德
from core.game import GameCard
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin


class E1(EffTriggerCostMixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2HAND, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if tp.args[0] is self.host:
                op = self.game.players[self.game.get_player(self.host).sp]
                return len(op.hand) > 0
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return (c in op.hand) & (c.ATK.add_val == amax)
        p = self.game.get_player(self.host)
        op = self.game.players[p.sp]
        amax = op.hand[0].ATK.add_val
        for c in op.hand:
            amax = max(c.ATK.add_val, amax)
        tgt = self.game.choose_target(p, p, check, self)
        if tgt is not None:
            self.host.ATK.change_adv(tgt.ATK.add_val)
            for i in range(0, 2):
                c = GameCard(self.game, ELocation.UNKNOWN + 2 - p.sp, tgt.cid, is_token=True)
                c.create(tgt.name, tgt.type, tgt.subtype, tgt.rank,
                         tgt.ATK.src_value, tgt.DEF.src_value)
                c.ATK.change_adv(0)
                self.game.send2hand(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
