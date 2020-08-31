# 实锤
from utils.common_effects import EffTriggerCostMixin
from utils.constants import EEffectDesc, ELocation, ECardType


class E1(EffTriggerCostMixin):
    """
    摧毁。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp is None:
            for p in self.game.players:
                for c in p.on_field:
                    if c is not None:
                        if (c.type == ECardType.EMPLOYEE) & (c.ATK.value == self.host.ATK.value):
                            return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.ATK.value == self.host.ATK.value) & \
                (c.type == ECardType.EMPLOYEE)

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
