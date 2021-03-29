# 对昨日的冥思
from utils.constants import EEffectDesc, ELocation
from core.game import GameCard
from models.effect import Effect


class E1(Effect):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2DECK, host=host, scr_arg=False)

    def condition(self, tp):
        if tp is None:
            for c in self.game.get_player(self.host).hand:
                # todo: 放入卡组不会被禁止吧？不会吧不会吧？
                # tp = TimePoint(ETimePoint.IN_DECK_END, self, [c, 1])
                # self.game.enter_time_point(tp)
                # if tp.args[-1]:
                return True
        return False

    def cost(self, tp):
        p = self.game.get_player(self.host)

        def check(c):
            return c.location == ELocation.HAND + 2 - p.sp
        cc = self.game.choose_target_from_func(p, p, check, self, True, False)
        if cc is not None:
            self.game.send2deck(p, p, cc, self)
            return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)
        c = GameCard(self.game, ELocation.UNKNOWN + 2 - p.sp, '87032772', is_token=True)
        c.ATK.change_adv(self.host.ATK.add_val, self)
        self.game.send2deck(p, p, c, self)

        f = False
        cs = list()
        for c in p.grave:
            if '冥思' in c.series:
                cs.append(c)
        for c in cs:
            self.game.send2exiled(p, p, c, self)
            f = True
        if f:
            c = GameCard(self.game, ELocation.UNKNOWN + 2 - p.sp, '23643378', is_token=True)
            c.ATK.change_adv(self.host.ATK.add_val, self)
            self.game.send2deck(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
