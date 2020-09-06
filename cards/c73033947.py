# 优秀竞争者
from utils.constants import EEffectDesc, ETimePoint
from models.effect import Effect
from core.game import TimePoint

from random import randint


class E1(Effect):
    """
    随机丢弃手牌并上升ATK。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.ATK_GAIN, host=host, trigger=True,
                         scr_arg=0)

    def condition(self, tp):
        if tp.tp == ETimePoint.SUCC_SUMMON:
            if (tp.sender is None) & (tp.args[0] is self.host):
                for c in self.game.get_player(self.host).hand:
                    tp = TimePoint(ETimePoint.TRY_DISCARD, self, [c, 1])
                    self.game.enter_time_point(tp)
                    if tp.args[-1]:
                        return True
        return False

    def cost(self, tp):
        # 至多3随机手牌丢弃
        if tp not in self.reacted:
            self.reacted.append(tp)
            p = self.game.get_player(self.host)
            m = p.req4num(1, min(3, len(p.hand)))
            if m is not None:
                for i in range(0, m):
                    # todo: 不会出现不能被丢弃的卡。
                    if len(p.hand):
                        self.game.discard(p, p, p.hand[randint(0, len(p.hand) - 1)], self)
                        self.scr_arg += 1
                    else:
                        break
                return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # ATK上升
        self.host.ATK.gain(self.scr_arg * 300, False, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
