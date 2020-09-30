# 对昨日的冥思
from utils.constants import EEffectDesc, ELocation
from core.game import GameCard
from models.effect import Effect


class E1(Effect):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SET_CARD, host=host)

    def condition(self, tp):
        if tp is None:
            p = self.game.get_player(self.host)
            for c in p.grave:
                if '冥思' in c.series:
                    return len(p.hand) > 0
        return False

    def cost(self, tp):
        p = self.game.get_player(self.host)
        f = False
        cs = list()
        for c in p.grave:
            if '冥思' in c.series:
                cs.append(c)
        for c in cs:
            self.game.send2exiled(p, p, c, self)
            f = True
        return f

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return c.location == ELocation.HAND + 2 - p.sp
        p = self.game.get_player(self.host)
        self.game.send2exiled(p, p, self.host, self)
        tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
        if tgt is not None:
            self.game.send2deck_above(p, p, tgt, self)
            cs = [GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '87032772', is_token=True),
                  GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '58142665', is_token=True),
                  GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '23643378', is_token=True)]
            for c in cs:
                c.ATK.change_adv(self.host.ATK.add_val, self)
            tgt = self.game.choose_target(p, p, [c.vid for c in cs], self, True, False)
            if tgt is not None:
                self.game.set_strategy(p, p, tgt, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
