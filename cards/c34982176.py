# 奇利亚诺
from utils.constants import EEffectDesc, ECardType, ELocation
from utils.common_effects import EffCommonSummon


class E1(EffCommonSummon):
    """
    交换场上1雇员的属性。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.PROPERTY_CHANGE, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target_from_func(p, p, check, self)
        if tgt is not None:
            atk = tgt.ATK.value
            tgt.ATK.become(tgt.DEF.value, False, self)
            tgt.DEF.become(atk, False, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
