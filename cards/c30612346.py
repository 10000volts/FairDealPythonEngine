# 离间
from core.game import TimePoint
from models.effect import Effect
from utils.constants import EEffectDesc, ELocation, ECardType, ETimePoint


class E1(Effect):
    """
    摧毁指定的雇员。
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
                    if c is not None and c.type == ECardType.EMPLOYEE and c.ATK.value >= self.host.ATK.value:
                        tp = TimePoint(ETimePoint.TRY_CHOOSE_TARGET, self, [c, 1])
                        self.game.enter_time_point(tp)
                        if tp.args[-1]:
                            return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return ((c.location & ELocation.ON_FIELD) > 0) & \
                    (c.type == ECardType.EMPLOYEE) & (c.ATK.value >= self.host.ATK.value)

        # 摧毁选择的卡
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
