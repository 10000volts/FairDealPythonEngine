# 末路抉择
from utils.common_effects import EffCommonStrategy
from utils.constants import EEffectDesc, ELocation


class E1(EffCommonStrategy):
    """
    摧毁指定的卡。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        return (tp is None) & (self.game.get_player(self.host).leader.DEF.value <= self.host.ATK.value)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()

        def check(c):
            return c.location & ELocation.ON_FIELD

        # 摧毁选择的卡
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self)
        if tgt is not None:
            self.game.destroy(self.host, tgt, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
