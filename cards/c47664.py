# 产品经理
from utils.common_effects import EffSummon
from utils.constants import EEffectDesc


class E1(EffSummon):
    """
    额外机会。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.EXTRA_CHANCE, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 本回合可额外发动1次策略
        p = self.game.get_player(self.host)
        p.activate_times += 1


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
