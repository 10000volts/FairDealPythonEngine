# 狂欢
from utils.common_effects import CommonStrategyEffect
from utils.constants import EEffectDesc, ECardType


class E1(CommonStrategyEffect):
    """
    ATK+EFF。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.PROPERTY_CHANGE, c=c)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()
        # 我方场上全部雇员ATK+EFF
        p = self.game.get_player(self.host)
        for em in p.on_field:
            if em is not None and em.type == ECardType.EMPLOYEE:
                if self.host.ATK.value < 800:
                    em.ATK.gain(self.host.ATK.value)
                else:
                    em.ATK.gain(800)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e1 = E1(c)
    c.register_effect(e1)
