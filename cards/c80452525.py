# 职业无赖
from core.game import TimePoint
from utils.constants import EEffectDesc, ECardType, ETimePoint
from utils.common_effects import EffTriggerCostMixin


class E1(EffTriggerCostMixin):
    """
    选择对方场上1雇员，其和这张卡ATK翻倍。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if (tp.args[0] is self.host) & (tp not in self.reacted):
                op = self.game.players[self.game.get_player(self.host).sp]
                for c in op.on_field:
                    if c is not None and c.type == ECardType.EMPLOYEE:
                        tp = TimePoint(ETimePoint.TRY_CHOOSE_TARGET, self, [c, 1])
                        self.game.enter_time_point(tp)
                        if tp.args[-1]:
                            return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return (c in op.on_field) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        op = self.game.players[p.sp]
        tgt = self.game.choose_target(p, p, check, self)
        if tgt is not None:
            tgt.ATK.plus(2)
            self.host.ATK.plus(2)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
