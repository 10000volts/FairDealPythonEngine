# 暴风新人
from utils.common_effects import EffCommonSummon
from utils.constants import EEffectDesc, ELocation, ECardType


class E1(EffCommonSummon):
    """
    摧毁场上全部策略。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        for c in self.game.vid_manager.get_cards():
            if ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.STRATEGY):
                self.game.destroy(self.host, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
