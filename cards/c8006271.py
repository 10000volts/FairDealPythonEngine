# 内部危机
from utils.common_effects import EffCommonStrategy
from utils.constants import EEffectDesc, ECardType


class E1(EffCommonStrategy):
    """
    ATK-EFF。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        op = self.game.players[self.game.get_player(self.host).sp]
        for em in op.on_field:
            if em is not None and em.type == ECardType.EMPLOYEE:
                em.ATK.gain(-self.host.ATK.value, False, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
