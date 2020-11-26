# 轮休
from utils.constants import EEffectDesc, ELocation
from models.effect import Effect


class E1(Effect):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2DECK, host=host, scr_arg=False)

    def condition(self, tp):
        return tp is None

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)

        def check(c):
            return c.location == ELocation.HAND + 2 - p.sp
        cs = self.game.choose_target_from_func(p, p, check, self, True, False, 0)
        if cs is not None:
            for cc in cs:
                cc.ATK.gain(200, False, self)
                self.game.send2deck(p, p, cc, self, len(p.deck) - 1)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
