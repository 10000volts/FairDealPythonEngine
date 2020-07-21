# 净心禅师
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType
from utils.common_effects import EffTriggerCostMixin, EffPerTurn, EffSummon


class E1(EffTriggerCostMixin):
    """
    不能攻击
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.INVALID, host=host, trigger=True, force=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.TRY_ATTACK:
            # 攻击者是自己
            if (tp.args[0] is self.host) & (tp not in self.reacted):
                return True
        return False

    def execute(self):
        # 无效
        self.reacted.pop().args[-1] = 0


class E2(EffPerTurn):
    """
    重置每回合的防止击溃次数。
    """
    def __init__(self, host):
        super().__init__(host=host, ef=E3(host))


class E3(EffTriggerCostMixin):
    """
    1次不会被击溃
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.INVALID, host=host, trigger=True, force=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.DESTROYING:
            # 是自己，是战斗摧毁
            if (tp.args[1] is self.host) & (tp.sender is None) & (tp not in self.reacted):
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()
        # 无效
        self.reacted.pop().args[-1] = 0
        self.host.remove_effect(self)


class E4(EffSummon):
    """
    复原属性。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.RESTORE, host=host,)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()

        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        # 选择目标，复原其属性
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self)
        if tgt is not None:
            tgt.ATK.reset()
            tgt.DEF.reset()


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
    c.register_effect(E3(c))
    c.register_effect(E4(c))
