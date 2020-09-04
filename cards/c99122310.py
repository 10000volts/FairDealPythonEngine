# 卡莉
from utils.constants import EEffectDesc
from utils.common_effects import EffCommonSummon


class E1(EffCommonSummon):
    """
    对对方玩家造成500伤害。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted.pop()。
        调用基类方法进行输出。
        :return:
        """
        # 给予对方500伤害
        p = self.game.players[self.game.get_player(self.host).sp]
        self.game.deal_damage(self.host, p.leader, 500, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
