# 工程师
from utils.constants import EEffectDesc, ECardType, ELocation, ETimePoint
from models.effect import Effect
from core.game import TimePoint


class E1(Effect):
    """
    ATK-1000。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.PROPERTY_CHANGE, host=host, trigger=True)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.SUCC_SUMMON and tp.args[0] is self.host:
            p = self.game.get_player(self.host)
            tp2 = TimePoint(ETimePoint.TRY_HP_COST, self, [p, 1000, 1])
            self.game.enter_time_point(tp2)
            if tp2.args[-1] & (p.leader.DEF.value > tp2.args[1]):
                return True
        return False

    def cost(self, tp):
        p = self.game.get_player(self.host)
        if tp not in self.reacted:
            self.reacted.append(tp)
            # 支付1000生命力
            f = p.leader.hp_cost(1000, self)
            if next(f):
                next(f)
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & (c.type == ECardType.EMPLOYEE)
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self)
        if tgt is not None:
            tgt.ATK.gain(-1000)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
