# 警员弗斯特
from utils.constants import EEffectDesc
from utils.common_effects import EffCommonSummon


class E1(EffCommonSummon):
    """
    摧毁策略。没有必要把条件判断写在条件里。
    """
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host)

    def execute(self):
        """
        执行效果。触发式效果获得当前时点信息时请使用reacted[-1]。
        调用基类方法进行输出。
        :return:
        """
        # 输出
        super().execute()
        pos = self.host.inf_pos
        op = self.game.players[self.game.get_player(self.host).sp]
        if (op.on_field[pos] is not None) & (op.on_field[pos + 3] is not None):
            self.game.destroy(self.host, op.on_field[pos + 3], self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
