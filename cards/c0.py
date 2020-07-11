# 默认领袖
from models.effect import Effect
from utils.constants import EEffectDesc, EGamePhase, ETimePoint


# class E2(Effect):
#     """
#     攻击力复原。
#     """
#     def __init__(self, c, op, v):
#         super().__init__(EEffectDesc.PROPERTY_CHANGE, EGamePhase.PLAY_CARD, c.game.get_player(c),
#                          c, True, True)
#         self.scr_arg = [op, v]
#
#     def condition(self):
#         """
#         是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
#         触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
#         :return:
#         """
#         if not super().condition():
#             return False
#
#         for tp in self.game.tp_stack[::-1]:
#             if tp.tp == ETimePoint.TURN_END and tp not in self.reacted:
#                 return True
#         return False
#
#     def cost(self):
#         """
#         支付cost，触发式效果需要在此添加连锁到的时点。
#         :return:
#         """
#         for tp in self.game.tp_stack[::-1]:
#             if tp.tp == ETimePoint.TURN_END and tp not in self.reacted:
#                 self.reacted.append(tp)
#                 return True
#
#     def execute(self):
#         """
#         执行效果。
#         :return:
#         """
#         self.host.ATK.remove(*self.scr_arg)
#         self.host.remove_effect(self)
#
#
# class E1(Effect):
#     """
#     自己的雇员入场后ATK+500。
#     """
#     def __init__(self, c):
#         super().__init__(EEffectDesc.PROPERTY_CHANGE, EGamePhase.PLAY_CARD, c.game.get_player(c),
#                          c, True, True)
#
#     def condition(self):
#         """
#         是否满足该效果发动的前提条件。尝试进行……效果的时点应在此处进行。
#         触发式效果需要额外判断所需的时点是否已被连锁过，否则会造成无限连锁或死循环。
#         :return:
#         """
#         if not super().condition():
#             return False
#
#         for tp in self.game.tp_stack[::-1]:
#             if tp.tp == ETimePoint.SUCC_SUMMON and self.host.game.get_player(tp.args[0]) is self.owner\
#                     and tp not in self.reacted:
#                 return True
#         return False
#
#     def cost(self):
#         """
#         支付cost，触发式效果需要在此添加连锁到的时点。
#         :return:
#         """
#         for tp in self.game.tp_stack[::-1]:
#             if tp.tp == ETimePoint.SUCC_SUMMON and self.host.game.get_player(tp.args[0]) is self.owner\
#                     and tp not in self.reacted:
#                 self.reacted.append(tp)
#                 return True
#
#     def execute(self):
#         """
#         执行效果。
#         :return:
#         """
#         tp = self.reacted[-1]
#         c = tp.args[0]
#         op, v = c.ATK.gain(500)
#         c.register_effect(E2(c, op, v))


def give(c):
    """
    将效果给予卡片。
    :param c:
    :return:
    """
    # e1 = E1(c)
    # c.register_effect(e1)
