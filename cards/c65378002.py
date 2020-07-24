# 新人策划
from utils.constants import EEffectDesc
from utils.common_effects import EffSummon, EffNextTurnMixin


class E2(EffNextTurnMixin):
    """
    本回合可额外使用1次策略。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.EXTRA_CHANCE, host=host, trigger=True, force=True,
                         no_reset=True)

    def execute(self):
        self.game.get_player(self.host).strategy_times += 1
        self.host.remove_effect(self)


class E1(EffSummon):
    """
    下次我方回合可额外使用1次策略。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.REGISTER_EFFECT, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 注册效果
        self.host.register_effect(E2(self.host), True)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
