# 洛斯
from models.effect import Effect
from core.game import TimePoint
from utils.constants import EEffectDesc, ETimePoint, ELocation


class E1(Effect):
    """
    从移除区入场。
    """
    def __init__(self, c):
        super().__init__(desc=EEffectDesc.SPECIAL_SUMMON,
                         host=c, no_reset=True, ef_id='951006560', scr_arg=[[ELocation.HAND, ELocation.GRAVE,
                                                                            ELocation.EXILED], None])

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp.tp == ETimePoint.ASK4EFFECT:
            sd = self.game.get_player(self.host)
            for posture in range(0, 2):
                for pos in range(0, 3):
                    if sd.on_field[pos] is None:
                        tp = TimePoint(ETimePoint.TRY_SUMMON, self, [self.host, sd, pos, posture, 1])
                        self.game.enter_time_point(tp)
                        # 入场被允许
                        if tp.args[-1]:
                            for loc in self.scr_arg[0]:
                                if (self.host.location & loc) > 0:
                                    self.scr_arg[1] = loc
                                    # 场上的卡恰好为5张
                                    count = 0
                                    for i in range(0, 6):
                                        for p in self.game.players:
                                            if p.on_field[i] is not None:
                                                count += 1
                                    return count == 5
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)
        self.game.special_summon(p, p, self.host, self)
        self.scr_arg[0].remove(self.scr_arg[1])


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    for ef in c.effects:
        if ef.ef_id == '951006560':
            return
    c.register_effect(E1(c))
