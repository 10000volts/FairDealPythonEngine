# 挫折大师
from utils.constants import EEffectDesc, ETimePoint, ELocation
from models.effect import Effect
from core.game import TimePoint


class E1(Effect):
    """
    丢弃手牌，从场下回收手牌。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2HAND, host=host, trigger=True)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if tp.args[0] is self.host:
                for c in self.game.get_player(self.host).hand:
                    tp = TimePoint(ETimePoint.TRY_DISCARD, self, [c, True, 1])
                    self.game.enter_time_point(tp)
                    if tp.args[-1]:
                        return True
        return False

    def cost(self, tp):
        # 选择1手牌丢弃
        self.reacted.append(tp)
        p = self.game.get_player(self.host)
        return self.game.req4discard(p, p, 1, self) is not None

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        p = self.game.get_player(self.host)

        def check(c):
            return (c.location == ELocation.GRAVE + 2 - p.sp) & (c.cid != '42993875')
        tgt = self.game.choose_target_from_func(p, p, check, self, True, False)
        # TODO: DELETE
        print(type(tgt.cid))
        if tgt is not None:
            self.game.send2hand(p, p, tgt, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
