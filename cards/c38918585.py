# 精神控制
from utils.common_effects import EffTriggerCostMixin
from utils.constants import EEffectDesc, ELocation, ECardType, ETimePoint


class E3(EffTriggerCostMixin):
    def __init__(self, host, p):
        super().__init__(desc=EEffectDesc.SEND2GRAVE, host=host, trigger=True, no_reset=True,
                         force=True, passive=True, scr_arg=p)

    def condition(self, tp):
        return tp.tp == ETimePoint.TURN_END

    def execute(self):
        p = self.game.get_player(self.host)
        self.game.send_to_grave(p, self.scr_arg, self.host, self)
        self.host.remove_effect(self)


class E2(EffTriggerCostMixin):
    """
    攻击后归还。
    """
    def __init__(self, host, p):
        super().__init__(desc=EEffectDesc.SEND2GRAVE, host=host, trigger=True, no_reset=True, force=True,
                         passive=True, scr_arg=p)

    def condition(self, tp):
        if tp is ETimePoint.ATTACKED:
            return tp.args[0] is self.host
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        :return:
        """
        self.host.register_effect(E3(self.host, self.scr_arg))
        self.host.remove_effect(self)


class E1(EffTriggerCostMixin):
    """
    控制。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.CONTROL, host=host)

    def condition(self, tp):
        if tp is None:
            p = self.game.get_player(self.host)
            op = self.game.players[p.sp]
            for pos in p.on_field:
                if p.on_field[pos] is None:
                    for c in op.on_field:
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
        tgt = self.game.choose_target_from_func(p, p, check, self)
        if tgt is not None:
            self.game.control(p, p, tgt, self)
            tgt.register_effect(E2(tgt, p))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
