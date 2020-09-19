# 激动的程序员
from utils.constants import EEffectDesc, ETimePoint, ELocation
from utils.common_effects import EffTriggerCostMixin


class E1(EffTriggerCostMixin):
    """
    自伤
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=c, trigger=True, force=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.SUCC_ACTIVATE_STRATEGY:
            # 自己在场，是对方的策略
            if ((self.host.location & ELocation.ON_FIELD) > 0) & \
                    ((tp.args[0].location & (self.game.get_player(self.host).sp + 1)) > 0):
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 受到伤害
        v = self.reacted.pop().args[0].ATK.value
        if v <= 1400:
            self.game.deal_damage(self.host, self.game.get_player(self.host).leader,
                                  v, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
