# 末日脉冲 克劳
from utils.constants import EEffectDesc, ECardType
from utils.common_effects import EffCommonSummon


class E1(EffCommonSummon):
    """
    摧毁场上的卡。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        for p in self.game.players:
            for c in p.on_field:
                if c is not None and c.type == ECardType.EMPLOYEE and c is not self.host:
                    if p.on_field[c.inf_pos + 3] is not None:
                        self.game.destroy(self.host, p.on_field[c.inf_pos + 3], self)
                    self.game.destroy(self.host, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
