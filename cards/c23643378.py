# 对明日的冥思
from utils.constants import EEffectDesc, ECardType, ELocation, ECardRank
from models.effect import Effect
from core.game import GameCard


class E1(Effect):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SET_CARD, host=host, scr_arg=False)

    def condition(self, tp):
        return tp is None
        #     p = self.game.get_player(self.host)
        #     for c in p.grave:
        #         if '冥思' in c.series:
        #             # for c2 in p.grave:
        #             #     if (c2.type == ECardType.STRATEGY) & (c2 is not c) & (c.rank < ECardRank.TRUMP):
        #             # 自身发动后会送入墓地所以总会有卡可被回收。
        #             return True
        # return False

    def cost(self, tp):
        p = self.game.get_player(self.host)
        cs = list()
        for c in p.grave:
            if '冥思' in c.series:
                cs.append(c)
        for c in cs:
            self.game.send2exiled(p, p, c, self)
            self.scr_arg = True
        return True

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)
        if self.scr_arg:
            self.game.send2exiled(p, p, self.host, self)

            def check(c):
                return (c.location == ELocation.GRAVE + 2 - p.sp) & (c.type == ECardType.STRATEGY) & \
                       (c.rank < ECardRank.TRUMP)
            tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
            if tgt is not None:
                self.game.set_strategy(p, p, tgt, self)
        # 弱化效果
        else:
            c = GameCard(self.game, ELocation.UNKNOWN + 2 - p.sp, '87032772', is_token=True)
            c.ATK.change_adv(self.host.ATK.add_val, self)
            self.game.send2deck(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
