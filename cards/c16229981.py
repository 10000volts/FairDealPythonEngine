# 业界前辈
from utils.constants import EEffectDesc, ETimePoint, ECardType, ELocation
from utils.common_effects import EffTriggerCostMixin


class E1(EffTriggerCostMixin):
    """
    摧毁场上策略。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if (tp.sender is None) & (tp not in self.reacted) & (tp.args[0] is self.host):
                for p in self.game.players:
                    for c in p.on_field:
                        if c is not None and c.type == ECardType.STRATEGY:
                            return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """

        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, lambda c: (((c.location & ELocation.ON_FIELD) > 0) &
                                                       (c.type == ECardType.STRATEGY)), self, True)
        self.game.destroy(self.host, tgt, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
