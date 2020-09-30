# 拖累
from models.effect import Effect
from utils.constants import EEffectDesc, ELocation, ECardType


class E1(Effect):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_LOSE, host=host)

    def condition(self, tp):
        if tp is None:
            op = self.game.players[self.game.get_player(self.host).sp]
            c = 0
            for c1 in op.on_field:
                if c1 is not None and c1.type == ECardType.EMPLOYEE:
                    c += 1
            return c > 1
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        op = self.game.players[p.sp]
        tgtA = self.game.choose_target_from_func(
            p, p, lambda c: ((c.location == ELocation.ON_FIELD + 2 - op.sp) &
                             (c.type == ECardType.EMPLOYEE)), self, True)
        if tgtA is not None:
            tgtB = self.game.choose_target_from_func(
                p, p, lambda c: ((c.location == ELocation.ON_FIELD + 2 - op.sp) &
                                 (c.type == ECardType.EMPLOYEE) & (c is not tgtA)), self, True)
            tgtB.ATK.gain(-tgtA.ATK.value, False, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
