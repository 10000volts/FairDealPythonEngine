# 伪造的录音笔
from utils.common_effects import EffCommonStrategy, EffExile
from utils.constants import EEffectDesc


class E2(EffExile):
    """
    我方场上的洛斯ATK+EFF(至多500)。
    """
    def __init__(self, host):
        super().__init__(host=host, desc=EEffectDesc.ATK_GAIN)

    def execute(self):
        p = self.game.get_player(self.host)
        for c in p.on_field:
            if c is not None and c.cid == '95100656':
                c.ATK.gain(min(self.host.ATK.value, 500), False, self)


class E1(EffCommonStrategy):
    """
    回收。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.SEND2GRAVE, host=host)

    def condition(self, tp):
        """
        是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
        触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
        :return:
        """
        if tp is None:
            p = self.game.get_player(self.host)
            for c in p.exiled:
                # 洛斯
                if c.cid == '95100656':
                    return True
        return False

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        def check(c):
            return (c in p.exiled) & (c.cid == '95100656')

        # 选择的卡回到墓地
        p = self.game.get_player(self.host)
        tgt = self.game.choose_target(p, p, check, self, False, False)
        if tgt is not None:
            self.game.send_to_grave(p, p, tgt, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
    c.register_effect(E2(c))
