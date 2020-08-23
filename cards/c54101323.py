# 模式切换
from utils.common_effects import EffTurnEndMixin, EffTriggerCostMixin, EffAttackLimit
from utils.constants import EEffectDesc, ECardType, ELocation, ETimePoint


class E2(EffTurnEndMixin):
    """
    回合结束时解除攻击限制。
    """
    def __init__(self, host, ef):
        super().__init__(desc=EEffectDesc.EFFECT_END,
                         host=host, trigger=True, force=True, scr_arg=ef, no_reset=True, passive=True)

    def execute(self):
        self.host.remove_effect(self.scr_arg)
        self.host.remove_effect(self)


class E1(EffTriggerCostMixin):
    """
    交换ATK/DEF。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=host)

    def condition(self, tp):
        from core.game import TimePoint
        if tp is None:
            # 我方场上存在可以成为效果对象的雇员
            p = self.game.get_player(self.host)
            for c in p.on_field:
                if c is not None:
                    if c.type == ECardType.EMPLOYEE:
                        # 模拟选择。
                        t = TimePoint(ETimePoint.TRY_CHOOSE_TARGET, self, [c, 1])
                        self.game.enter_time_point(t)
                        if t.args[-1]:
                            return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self, True)
        if tgt is not None:
            atk = tgt.ATK.value
            tgt.ATK.become(tgt.DEF.value)
            tgt.DEF.become(atk)
            e3 = EffAttackLimit(tgt, False)
            tgt.register_effect(e3)
            tgt.register_effect(E2(tgt, e3))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
