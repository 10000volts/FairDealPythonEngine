# 涨薪
from core.game import TimePoint
from models.effect import Effect
from utils.common_effects import EffCommonStrategy, EffTurnEndMixin
from utils.constants import EEffectDesc, ECardType, ETimePoint, ELocation, EGamePhase


class E2(EffTurnEndMixin):
    """
    回合结束时回复攻击力。
    """
    def __init__(self, host, c, op, v):
        super().__init__(desc=EEffectDesc.EFFECT_END, act_phase=EGamePhase.PLAY_CARD,
                         host=host, trigger=True, force=True, scr_arg=[c, op, v], no_reset=True)

    def execute(self):
        self.scr_arg[0].ATK.remove(self.scr_arg[1], self.scr_arg[2])
        self.host.remove_effect(self)


class E1(EffCommonStrategy):
    """
    ATK+EFF(至少500)。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=host)

    def condition(self, tp):
        if tp is None:
            # 场上存在可以成为效果对象的雇员
            for p in self.game.players:
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
        # 输出
        super().execute()

        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        # 选择1雇员ATK+EFF(至少500)直到回合结束
        tgt = self.game.choose_target(check, self)
        if tgt is not None:
            op, v = tgt.ATK.gain(500 if self.host.ATK.value < 500 else self.host.ATK.value)
            self.host.register_effect(E2(self.host, tgt, op, v))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
