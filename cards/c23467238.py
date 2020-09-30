# 察觉
from utils.common_effects import EffCommonStrategy
from utils.constants import EEffectDesc, ELocation, ECardType, EStrategyType


class E1(EffCommonStrategy):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp is None:
            op = self.game.players[self.game.get_player(self.host).sp]
            for c in op.on_field:
                if c is not None and c.type == ECardType.STRATEGY:
                    return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return (c.location == ELocation.ON_FIELD + 2 - op.sp) & (c.type == ECardType.STRATEGY)

        # 摧毁选择的卡
        p = self.game.get_player(self.host)
        op = self.game.players[p.sp]
        tgt = self.game.choose_target_from_func(p, op, check, self)
        if tgt.subtype & EStrategyType.COUNTER:
            p.strategy_times += 1
        self.game.destroy(self.host, tgt, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
