# 违约金
from models.effect import Effect
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType
from utils.common_effects import EffTriggerCostMixin, EffCommonStrategy


class E1(EffCommonStrategy):
    """
    给予伤害。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=c)

    def execute(self):
        pass


class E2(Effect):
    """
    给予伤害。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=c, trigger=True, force=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.OUT_FIELD:
            if ((self.host.location & ELocation.ON_FIELD) > 0) & (not self.host.cover) &\
                    (tp not in self.reacted) & (tp.args[0].type == ECardType.EMPLOYEE):
                return True
        return False

    def cost(self, tp):
        self.reacted.append(tp)
        return True

    def execute(self):
        # 输出
        super().execute()

        c = self.reacted.pop().args[0]
        pt = self.game.get_player(c)
        self.game.deal_damage(self.host, pt.leader, int(c.ATK.value / 2), self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
