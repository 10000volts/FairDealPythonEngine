# 私法制裁者
from utils.common_effects import EffSummon
from utils.constants import EEffectDesc, ECardType


class E1(EffSummon):
    def __init__(self, host):
        super().__init__(desc=EEffectDesc.DESTROY, host=host)

    def execute(self):
        for p in self.game.players:
            for em in p.on_field:
                if em is not None and em.type == ECardType.EMPLOYEE:
                    if '臭名昭著' in em.series:
                        self.game.destroy(self.host, em, self)


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    c.register_effect(E1(c))
