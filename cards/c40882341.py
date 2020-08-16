# 继承
from models.effect import Effect
from utils.constants import EEffectDesc, ETimePoint, ELocation, ECardType
from core.game import TimePoint
from utils.common_effects import EffNextTurnMixin, EffTriggerCostMixin


class E3(EffTriggerCostMixin):
    """
    造成的战斗伤害减半。
    """
    def __init__(self, c, scr_arg):
        super().__init__(desc=EEffectDesc.DAMAGE_CHANGE,
                         host=c, trigger=True, force=True, scr_arg=scr_arg)

    def condition(self, tp):
        if tp.tp == ETimePoint.DEALING_DAMAGE:
            if (tp.args[0] is self.scr_arg) & (tp.sender is None) & (tp not in self.reacted):
                return True
        return False

    def execute(self):
        tp = self.reacted.pop()
        tp.args[2] = int(tp.args[2] / 2)


class E2(EffNextTurnMixin):
    """
    回合开始时时回复攻击力和造成战斗伤害减半效果。
    """
    def __init__(self, host, c, op, v, ef):
        super().__init__(desc=EEffectDesc.EFFECT_END,
                         host=host, trigger=True, force=True, scr_arg=[c, op, v, ef], no_reset=True,
                         passive=True)

    def execute(self):
        self.scr_arg[0].ATK.remove(self.scr_arg[1], self.scr_arg[2])
        self.host.remove_effect(self.scr_arg[3])
        self.host.remove_effect(self)


class E1(Effect):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=host, scr_arg=0)

    def condition(self, tp):
        if tp is None:
            p = self.game.get_player(self.host)
            for c1 in p.on_field:
                if c1 is not None and c1.type == ECardType.EMPLOYEE:
                    tp = TimePoint(ETimePoint.TRY_DEVOTRE, self, [c1, 1])
                    self.game.enter_time_point(tp)
                    if tp.args[-1]:
                        for p in self.game.players:
                            for c in p.on_field:
                                if c is not None and c is not c1 and c.type == ECardType.EMPLOYEE:
                                    tp = TimePoint(ETimePoint.TRY_CHOOSE_TARGET, self, [c, 1])
                                    self.game.enter_time_point(tp)
                                    if tp.args[-1]:
                                        return True
        return False

    def cost(self, tp):
        # 奉献
        p = self.game.get_player(self.host)

        def check(_c):
            if _c not in p.on_field or _c.type != ECardType.EMPLOYEE:
                return False
            tp1 = TimePoint(ETimePoint.TRY_DEVOTRE, self, [_c, 1])
            self.game.enter_time_point(tp1)
            return tp1.args[1]
        # 奉献是cost，不取对象
        # 有特殊处理，不能使用默认的奉献函数
        c1 = self.game.choose_target(p, p, check, self, False, False)
        if c1 is not None:
            tp = TimePoint(ETimePoint.DEVOTING, self, [c1, 1])
            self.game.enter_time_point(tp)
            if tp.args[-1]:
                self.scr_arg = c1.ATK.value
                self.game.send_to_grave(p, p, c1, self)
                self.game.enter_time_point(TimePoint(ETimePoint.DEVOTED, self, [c1]))
                return True
        return False

    def execute(self):
        p = self.game.get_player(self.host)
        for p in self.game.players:
            for c in p.on_field:
                if c is not None and c.type == ECardType.EMPLOYEE:
                    tp = TimePoint(ETimePoint.TRY_CHOOSE_TARGET, self, [c, 1])
                    self.game.enter_time_point(tp)
                    if tp.args[-1] == 0:
                        return
        tgt = self.game.choose_target(p, p, lambda c: (((c.location & ELocation.ON_FIELD) > 0) &
                                                      (c.type == ECardType.EMPLOYEE)), self, True)
        if tgt is not None:
            op, v = tgt.ATK.gain(self.scr_arg)
            e3 = E3(self.host, tgt)
            self.host.register_effect(e3)
            self.host.register_effect(E2(self.host, tgt, op, v, e3))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
