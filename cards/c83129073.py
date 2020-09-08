# 帮派成员
from utils.constants import EEffectDesc, ECardType, ELocation
from utils.common_effects import EffCommonSummon


class E1(EffCommonSummon):
    """
    失去生命力，摧毁场上1雇员。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self)
        if tgt is not None:
            self.game.get_player(self.host).leader.DEF.gain(-tgt.ATK.value, False, self)
            self.game.destroy(self.host, tgt, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
