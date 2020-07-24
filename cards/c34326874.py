# 拒绝服务攻击
from utils.common_effects import EffCommonStrategy
from utils.constants import EEffectDesc, ECardType


class E1(EffCommonStrategy):
    """
    给予伤害。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DEAL_DAMAGE, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 对对方造成EFF伤害
        op = self.game.players[self.game.get_player(self.host).sp]
        self.game.deal_damage(self.host, op.leader, self.host.ATK.value)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
