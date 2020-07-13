# 末路抉择
from utils.common_effects import CommonStrategyEffect
from utils.constants import EEffectDesc, ELocation


class E1(CommonStrategyEffect):
    """
    摧毁指定的卡。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DESTROY, c=c)

    def condition(self):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        return self.game.get_player(self.host).leader.DEF.value <= self.host.ATK.value

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()

        def func(c):
            return c.location & ELocation.ON_FIELD

        # 摧毁选择的卡
        tgt = self.game.choose_target(func, self.host, self)
        if tgt is not None:
            self.game.destroy(self.host, tgt, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e1 = E1(c)
    c.register_effect(e1)
