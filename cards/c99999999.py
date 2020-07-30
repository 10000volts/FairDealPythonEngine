# 飞天拉面神
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType
from utils.common_effects import EffPierce, EffTriggerCostMixin


class E4(Effect):
    """
    奉献。
    """


class E2(Effect):
    """
    从手牌入场。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON, host=c)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        # todo: 不会设计能无效移除的效果
        def dp(v, i):
            if v == self.host.ATK.value:
                return True
            if i == len(ems):
                return False
            return dp(v + ems[i], i + 1) | dp(v, i + 1)

        if tp.tp == ETimePoint.ASK4EFFECT:
            if self.host.location & ELocation.HAND:
                p = self.game.get_player(self.host)
                for posture in range(0, 2):
                    for pos in range(0, 3):
                        # 不用检查是否有空格子
                        tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, p, pos, posture, 1])
                        self.game.enter_time_point(tp)
                        # 入场被允许
                        if tp.args[-1]:
                            ems = list()
                            for c in p.on_field:
                                if c is not None and c.type == ECardType.EMPLOYEE:
                                    ems.append(c.ATK.value)
                            # 问题规模不需要dp, 过于占用空间
                            return dp(0, 0)
        return False

    def cost(self, tp):
        p = self.game.get_player(self.host)

        def check(_c):
            # todo: 因为是cost，所以在自己场上的雇员一定能被移除。
            return (_c in p.on_field) & (_c.type == ECardType.EMPLOYEE)

        # 是cost，不取对象
        # 先选好，再移除
        atk = 0
        while True:
            c1 = self.game.choose_target(p, p, check, self, False, False)
            if c1 is not None:

                tp = TimePoint(ETimePoint.DEVOTING, self, [c1, 1])
                self.game.enter_time_point(tp)
                if tp.args[-1]:
                    self.scr_arg = c1.ATK.value
                    self.game.send_to_grave(p, p, c1, self)
                    self.game.enter_time_point(TimePoint(ETimePoint.DEVOTED, self, [c1]))
                    return True
            else:
                return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 入场
        p = self.game.get_player(self.host)
        self.game.special_summon(p, p, self.host, self)
        # 我方受到的伤害减半
        e3 = E3(self.host, p.leader)
        self.host.register_effect(e3, True)


class E1(EffTriggerCostMixin):
    """
    不能通过自身效果以外的方式入场。
    """
    def __init__(self, c, ef):
        super().__init__(desc=EEffectDesc.INVALID,
                         host=c, trigger=True, force=True, scr_arg=ef, passive=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.TRY_SUMMON:
            if (tp.args[0] is self.host) & \
                    (tp.sender is not self.scr_arg) & (tp not in self.reacted):
                return True
        return False

    def execute(self):
        # 禁止入场。
        self.reacted.pop().args[-1] = 0


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    e2 = E2(c)
    c.register_effect(e2)
    c.register_effect(E1(c, e2))
    c.register_effect(EffPierce(c))
    c.register_effect(E4(c))
