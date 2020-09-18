# 对今日的冥思
from utils.common_effects import EffSingleStgE1Mixin
from utils.constants import EEffectDesc, ECardType, ELocation


class E1(EffSingleStgE1Mixin):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.INVALID, host=host)

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
            count = 0
            for c in p.grave:
                if '冥思' in c.series:
                    self.game.send2exiled(p, p, c, self)
                    count += 1
            tgt.ATK.gain(self.host.ATK.value if count * 300 > self.host.ATK.value else count * 300, False, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
