# 枪械艺术家
from utils.constants import ETimePoint, EEffectDesc, ELocation, ECardType, EStrategyType, EChoice
from models.effect import Effect
from core.game import GameCard


class E1(Effect):
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.SEND2HAND)

    def condition(self, tp):
        if tp.tp == ETimePoint.ASK4EFFECT:
            if (self.host.location & ELocation.ON_FIELD) > 0:
                p = self.game.get_player(self.host)
                for c in p.grave:
                    if (c.type == ECardType.STRATEGY) & ((c.subtype & EStrategyType.ATTACHMENT) > 0):
                        return True
        return False

    def cost(self, tp):
        p = self.game.get_player(self.host)

        def check(c):
            return (c.location == ELocation.GRAVE + 2 - p.sp) & (c.type == ECardType.STRATEGY) & \
                   ((c.subtype & EStrategyType.ATTACHMENT) > 0)
        c = self.game.req4exile(check, p, p, 1, self)
        if c is not None:
            self.scr_arg = c.ATK.add_val
            return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        cs = [GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '50526002', is_token=True),
              GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '50526002', is_token=True),
              GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '82751803', is_token=True)]
        for c in cs:
            c.ATK.change_adv(self.scr_arg)
        tgt = self.game.choose_target(p, p, cs, self, True, False)
        if tgt is not None:
            self.game.send2hand(p, p, tgt, self)
        # r = p.req4option([EChoice.C50526002, EChoice.C79047277, EChoice.C82751803])
        # if r == EChoice.C50526002:
        #     c = GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '50526002', is_token=True)
        #     c.ATK.change_adv(self.scr_arg)
        #     self.game.send2hand(p, p, c, self)
        # elif r == EChoice.C79047277:
        #     c = GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '79047277', is_token=True)
        #     c.ATK.change_adv(self.scr_arg)
        #     self.game.send2hand(p, p, c, self)
        # else:
        #     c = GameCard(self.game, ELocation.UNKNOWN | (2 - p.sp), '82751803', is_token=True)
        #     c.ATK.change_adv(self.scr_arg)
        #     self.game.send2hand(p, p, c, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
