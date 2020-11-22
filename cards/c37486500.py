# 末日脉冲 克劳
from utils.constants import EEffectDesc, ECardType, ETimePoint
from utils.common_effects import EffCommonSummon


class E1(EffCommonSummon):
    """
    摧毁场上的卡。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host, ef_id='374865000')

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.SUCC_SUMMON:
            return (tp.args[0] is self.host) & (tp.sender is None) & \
                   (self.ef_id not in self.game.get_player(self.host).ef_g_limiter)
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        for p in self.game.get_players():
            for c in p.on_field:
                if c is not None and c.type == ECardType.EMPLOYEE and c is not self.host:
                    if p.on_field[c.inf_pos + 3] is not None:
                        self.game.destroy(self.host, p.on_field[c.inf_pos + 3], self)
                    self.game.destroy(self.host, c, self)
        self.game.get_player(self.host).ef_g_limiter[self.ef_id] = 1


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
