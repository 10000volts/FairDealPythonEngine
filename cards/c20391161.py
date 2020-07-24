# 你的超人老妈
from utils.constants import EEffectDesc, ELocation
from utils.common_effects import EffCommonSummon


class E1(EffCommonSummon):
    """
    从场下回收手牌。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2HAND, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)

        def check(c):
            return c in p.grave
        tgt = self.game.choose_target(p, p, check, self, False, False)
        if tgt is not None:
            self.game.send2hand(p, p, tgt, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
