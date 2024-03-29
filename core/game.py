# todo: 优化upd_vc，使其可以支持只传部分参数

from utils.constants import ECardRank, ECardType, ELocation, ETimePoint,\
    EGamePhase, ETurnPhase, EErrorCode, EEmployeeType, EStrategyType
from utils.common import adj_pos
from utils.common_effects import EffInvestigator
from models.player import Player
from core.io import input_from_socket, input_from_local, input_from_ai, output_2_socket,\
    output_2_local, output_2_ai, set_socket, make_output, make_input
from models.effect import Effect

from importlib import import_module
from random import randint
import redis
import json
from datetime import datetime
from threading import Thread
from time import sleep

# redis键值对int/str不敏感
rds = redis.StrictRedis(db=0)


class GamePlayer:
    """
    游戏中的玩家。
    """
    def __init__(self, p: Player, deck: dict, leader_card_id: int):
        self.game = None

        def method_convert(om):
            if om == 'local':
                return input_from_local, output_2_local
            elif om == 'from_network':
                set_socket(p.upstream)
                return input_from_socket, output_2_socket
            else:
                m = import_module('ai.ai_{}'.format(p.upstream))

                return input_from_ai, output_2_ai
        # op_method的acceptor
        self.upstream = p.upstream
        m = method_convert(p.op_method)
        self.in_method = m[0]
        self.out_method = m[1]
        self.auto_skip = p.auto_skip
        self.ori_deck = deck
        self.deck = list()
        self.ori_side = list()
        self.side = list()
        # 手牌
        self.hand = list()
        self.grave = list()
        # 除外区
        self.exiled = list()
        # 场上
        self.on_field = [None, None, None, None, None, None]
        self.leader: GameCard = None
        self.leader_id = leader_card_id
        # 可使雇员从手牌通常入场的剩余次数。通常情况下每回合1次。
        self.summon_times = 1
        # 可从手牌使用策略的剩余次数。通常情况下每回合1次。
        self.strategy_times = 1
        # 可从手牌额外发动策略的剩余次数。通常情况下每回合0次。
        self.activate_times = 0
        # 可从手牌额外盖放策略的剩余次数。通常情况下每回合0次。
        self.set_times = 0
        # 是否为先手玩家。
        self.sp = 0
        # 回合效果限定器。{ef_id: times, ...}
        self.ef_limiter = dict()
        # 效果限定器。{ef_id: times, ...}
        self.ef_g_limiter = dict()

    def init_game(self, g):
        """
        初始化/重置游戏
        :param g:
        :param p_loc:
        :return:
        """
        self.game = g

        self.sp = int(g.p1 is self)
        self.leader = GameCard(g, ELocation.UNKNOWN + 2 - self.sp, self.leader_id)
        hd = list()
        sd = list()
        for cid in self.ori_deck.keys():
            for i in range(self.ori_deck[cid][0]):
                gc = GameCard(g, ELocation.HAND + 2 - self.sp, cid)
                hd.append(gc)
            for i in range(self.ori_deck[cid][1]):
                gc = GameCard(g, ELocation.SIDE + 2 - self.sp, cid)
                sd.append(gc)
        self.deck = list()
        self.ori_side = sd
        self.side = sd
        # 手牌
        self.hand = hd
        self.on_field = [None, None, None, None, None, None]
        self.grave = list()
        self.exiled = list()
        # 清空效果限制
        self.ef_limiter = dict()
        self.ef_g_limiter = dict()

    def input(self, func, *args):
        return self.in_method(self, make_input(*args), func, self.game.give_up)

    def free_input(self, func, *args):
        return self.in_method(self, make_input(*args), func, self.game.give_up, False)

    def output(self, *args):
        msg = make_output(*args)
        # 与之对应，输入不需要记录。
        if self.game is not None:
            self.game.record(self, msg)
        self.out_method(self.upstream, msg)

    def init_card_info(self):
        """
        向客户端发送初始化卡片请求。
        :return:
        """
        # 传输领袖信息。
        self.update_vc(self.leader)
        for c in self.hand:
            self.update_vc(c)
        for c in self.side:
            self.update_vc(c)
        for p in self.game.players:
            self.output('upd_vc', [p.leader.vid, p.leader.serialize()], self is p)
            if p != self:
                for c in p.hand:
                    self.update_vc_ano(c)
                for c in p.side:
                    self.update_vc_ano(c)

    def req4option(self, option: list, count=1, force=False):
        """
        从给定的选项中选择。
        :param count:
        :param force:
        :param option:
        :return:
        """
        def check(*_ind):
            if (count == 0) | (len(_ind) == count):
                for i in _ind:
                    if i not in option:
                        return EErrorCode.OVERSTEP
                return 0
            return EErrorCode.ILLEGAL_OPTIONS

        if force:
            return self.input(check, 'req_chs', [option, count])
        else:
            return self.free_input(check, 'req_chs', [option, count])

    def req4num(self, min, max, force=False):
        """
        从给定的数字中选择。
        :param min:
        :param max:
        :param force:
        :return:
        """
        def check(*_ind):
            for i in _ind:
                if i not in range(min, max + 1):
                    return EErrorCode.OVERSTEP
            return 0
        if force:
            return self.input(check, 'req_num', [min, max])
        else:
            return self.free_input(check, 'req_num', [min, max])

    def shuffle(self, loc=ELocation.HAND):
        def shu(ls):
            if sort:
                st = list()
                em = list()
                for c in ls:
                    if c.type == ECardType.STRATEGY:
                        st.append(c)
                    else:
                        em.append(c)
                _len = len(em) - 1
                for i in range(0, _len + 1):
                    ind = randint(0, _len)
                    temp = em[i]
                    em[i] = em[ind]
                    ls[i] = em[i]
                    em[ind] = temp
                    ls[ind] = temp
                _len = len(st) - 1
                for i in range(0, _len + 1):
                    ind = randint(0, _len)
                    temp = st[i]
                    st[i] = st[ind]
                    ls[i + len(em)] = st[i]
                    st[ind] = temp
                    ls[ind + len(em)] = temp
            else:
                _len = len(ls) - 1
                for i in range(0, _len + 1):
                    ind = randint(0, _len)
                    temp = ls[i]
                    ls[i] = ls[ind]
                    ls[ind] = temp

        cs = list()
        if loc == ELocation.HAND:
            cs = self.hand
            sort = True
        elif loc == ELocation.DECK:
            cs = self.deck
        elif loc == ELocation.SIDE:
            cs = self.side
        for c in cs:
            c.cover = 1
            self.game.vid_manager.change(c.vid)
        shu(cs)
        # g: Game = self.game
        for p in self.game.players:
            p.output('shf', [loc + 2 - self.sp])
            if p is self:
                for c in cs:
                    self.update_vc(c)
            else:
                for c in cs:
                    p.update_vc_ano(c)

    def update_vc(self, c):
        self.output('upd_vc', [c.vid, c.serialize()])

    def update_vc_ano(self, c):
        self.output('upd_vc_ano', [c.vid, c.serialize_anonymous()])


class Value:
    def __init__(self, v):
        self.value = v


class CardProperty:
    def __init__(self, v, tp0, tp1, tp2, c):
        """

        :param v: 初始值。
        :param tp0: 计算src_atk时触发的时点。
        :param tp1: 计算该属性时触发的时点。
        :param tp2: 计算该属性后触发的时点。
        :param c: GameCard
        """
        self.src_value = v
        # 不能在类外修改。方便起见没有进行封装。
        self.value = v
        # 附加值。additional value
        self.add_val = 0
        # 运算符栈。包含+、*、=(变成)、++(永久上升)、**、==、+x(上升不定值)、*x、=x、++x、**x、==x
        self.op_st = list()
        # 数值栈。
        self.val_st = list()
        self.tp0 = tp0
        self.tp1 = tp1
        self.tp2 = tp2
        self.card = c

    def reset(self):
        i = 0
        while i < len(self.op_st):
            if self.op_st[i].value in '+*=+x*x=x':
                self.op_st.pop(i)
                self.val_st.pop(i)
                i -= 1
            i += 1
        self.update()

    def update(self):
        v = self.src_value
        g = self.card.game
        if self.tp0 is not None:
            tp = TimePoint(self.tp0, None, [self.card, self.add_val])
            g.enter_time_point(tp)
            v += tp.args[1]
        else:
            v += self.add_val
        if v < 0:
            v = 0
        i = 0
        for op in self.op_st:
            _op = op.value
            if (_op == '+') | (_op == '++'):
                v += self.val_st[i]
            elif (_op == '*') | (_op == '**'):
                v *= self.val_st[i]
            elif (_op == '=') | (_op == '=='):
                v = self.val_st[i]
            elif (_op == '+x') | (_op == '++x'):
                # 回调函数。
                x = self.val_st[i]
                v += x(self.card)
            elif (_op == '*x') | (_op == '**x'):
                x = self.val_st[i]
                v *= x(self.card)
            elif (_op == '=x') | (_op == '==x'):
                x = self.val_st[i]
                v = x(self.card)
            if v < 0:
                v = 0
            i += 1
        self.value = v if v > 0 else 0
        t1 = TimePoint(self.tp1, None, [self.card, self.value])
        g.enter_time_point(t1)
        self.value = int(t1.args[1]) if t1.args[1] > 0 else 0
        g.enter_time_point(TimePoint(self.tp2, None, [self.card, self.value]))
        # 发送属性更新信息。
        for p in self.card.game.players:
            if (p is g.get_player(self.card)) | (self.card.cover == 0):
                p.update_vc(self.card)
            else:
                p.update_vc_ano(self.card)

    def gain(self, v, perm: bool = False, ef: Effect = None):
        """
        攻击力上升/下降。
        :param v:
        :param perm: 是否永久。
        :param ef:
        :return:
        """
        flag = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [self.card, 1])
            self.card.game.enter_time_point(tp)
            flag = tp.args[-1]
        if flag:
            new_op = Value('++' if perm else '+')
            self.op_st.append(new_op)
            self.val_st.append(v)
            self.update()
            return new_op, v
        return None, None

    def gain_x(self, x, perm: bool = False, ef: Effect = None):
        flag = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [self.card, 1])
            self.card.game.enter_time_point(tp)
            flag = tp.args[-1]
        if flag:
            new_op = Value('++x' if perm else '+x')
            self.op_st.append(new_op)
            self.val_st.append(x)
            self.update()
            return new_op, x
        return None, None

    def become(self, v, perm: bool = False, ef: Effect = None):
        flag = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [self.card, 1])
            self.card.game.enter_time_point(tp)
            flag = tp.args[-1]
        if flag:
            new_op = Value('==' if perm else '=')
            self.op_st.append(new_op)
            self.val_st.append(v)
            self.update()
            return new_op, v
        return None, None

    def become_x(self, x, perm: bool = False, ef: Effect = None):
        flag = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [self.card, 1])
            self.card.game.enter_time_point(tp)
            flag = tp.args[-1]
        if flag:
            new_op = Value('==x' if perm else '=x')
            self.op_st.append(new_op)
            self.val_st.append(x)
            self.update()
            return new_op, x
        return None, None

    def plus(self, v, perm: bool = False, ef: Effect = None):
        flag = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [self.card, 1])
            self.card.game.enter_time_point(tp)
            flag = tp.args[-1]
        if flag:
            new_op = Value('**' if perm else '*')
            self.op_st.append(new_op)
            self.val_st.append(v)
            self.update()
            return new_op, v
        return None, None

    def plus_x(self, x, perm: bool = False, ef: Effect = None):
        flag = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [self.card, 1])
            self.card.game.enter_time_point(tp)
            flag = tp.args[-1]
        if flag:
            new_op = Value('**x' if perm else '*x')
            self.op_st.append(new_op)
            self.val_st.append(x)
            self.update()
            return new_op, x
        return None, None

    def remove(self, op, v):
        for i in range(0, len(self.op_st)):
            if self.op_st[i] is op:
                self.op_st.pop(i)
                self.val_st.pop(i)
                self.update()
                return

    def change_adv(self, adv, ef: Effect = None):
        flag = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [self.card, 1])
            self.card.game.enter_time_point(tp)
            flag = tp.args[-1]
        if flag:
            self.add_val = adv
            self.update()


class HPProperty(CardProperty):
    def update(self):
        super().update()
        # HP不存储过程。
        self.op_st = [Value('=')]
        self.val_st = [self.value]
        if self.value <= 0:
            self.card.game.destroy(None, self.card)


class GameCard:
    def __init__(self, g, ori_loc, cid=None, is_token=False):
        """

        :param cid:
        :param ori_loc: 初始位置。
        :param is_token:
        """
        # visual id 模拟实际的玩家视野，洗牌等行为后vid改变
        self.game = g
        self.location = ori_loc
        self.vid = 0
        g.vid_manager.register(self)
        if cid is not None:
            self.cid = cid
            self.name = rds.hget(cid, 'name').decode()
            self.type = int(rds.hget(cid, 'type').decode())
            self.subtype = int(rds.hget(cid, 'subtype').decode())
            self.rank = int(rds.hget(cid, 'rank').decode())
            # 不可修改。
            self.src_atk = int(rds.hget(cid, 'atk_eff').decode())
            self.src_def = int(rds.hget(cid, 'def_hp').decode())
            self.ATK = CardProperty(self.src_atk, ETimePoint.SRC_ATK_CALCING,
                                    ETimePoint.ATK_CALCING, ETimePoint.ATK_CALC, self)
            if self.type == ECardType.LEADER:
                self.DEF = HPProperty(self.src_def, None,
                                      ETimePoint.DEF_CALCING, ETimePoint.DEF_CALC, self)
                self.cover = 0
            else:
                self.DEF = CardProperty(self.src_def, None,
                                        ETimePoint.DEF_CALCING, ETimePoint.DEF_CALC, self)
                # 是否被暗置(背面朝上，对对方玩家不可见)。
                self.cover = 1
            self.series = json.loads(rds.hget(cid, 'series').decode())
            self.is_token = is_token
            self.effects = list()
            # 在对局中获得的效果。{eff: desc}
            self.buff_eff = dict()
            # in field position 在自己场上的位置。0-2: 雇员区 3-5: 策略区
            self.inf_pos = 0
            # 场上的姿态。非零表示防御姿态。
            self.posture = 0
            # 是否拥有"风行"效果
            self.charge = False
            # 能否被随机放下
            self.can_random_put = True
            # 剩余攻击次数(入场、回合开始时重置)。为负数则可无限次数攻击。
            self.attack_times = 0
            # 剩余阻挡次数(入场、回合开始时重置)。为负数则可无限次数阻挡。
            self.block_times = 0
            # 剩余可改变姿态次数(回合开始时重置)。为负数则可无限次数改变。
            self.posture_times = 0
            # 经历过的回合数(回合结束时自动+1)。
            self.turns = 0
            # 标识
            self.sign = dict()
            m = import_module('cards.c{}'.format(self.cid))
            m.give(self)
        else:
            self.cid = None
            self.effects = list()

    def create(self, name, ty, subtype, rank, src_atk, src_def):
        """
        token的初始化
        :param g:
        :param name:
        :param ty:
        :param subtype:
        :param rank:
        :param src_atk:
        :param src_def:
        :param ori_loc:
        """
        # visual id 模拟实际的玩家视野，洗牌等行为后vid改变
        self.name = name
        self.type = ty
        self.subtype = subtype
        self.rank = rank
        # 不可修改。
        self.src_atk = src_atk
        self.src_def = src_def
        self.ATK = CardProperty(self.src_atk, ETimePoint.SRC_ATK_CALCING,
                                ETimePoint.ATK_CALCING, ETimePoint.ATK_CALC, self)
        self.DEF = CardProperty(self.src_def, None,
                                ETimePoint.DEF_CALCING, ETimePoint.DEF_CALC, self)
        # 是否被暗置(背面朝上，对对方玩家不可见)。
        self.cover = 0
        self.series = list()
        self.is_token = True
        # 在对局中获得的效果。{eff: desc}
        self.buff_eff = dict()
        # in field position 在自己场上的位置。0-2: 雇员区 3-5: 策略区
        self.inf_pos = 0
        # 场上的姿态。非零表示防御姿态。
        self.posture = 0
        # 是否拥有"风行"效果
        self.charge = False
        # 剩余攻击次数(入场、回合开始时重置)。为负数则可无限次数攻击。
        self.attack_times = 0
        # 剩余阻挡次数(入场、回合开始时重置)。为负数则可无限次数阻挡。
        self.block_times = 0
        # 剩余可改变姿态次数(回合开始时重置)。为负数则可无限次数改变。
        self.posture_times = 0
        # 经历过的回合数(回合结束时自动+1)。
        self.turns = 0
        # 标识
        self.sign = dict()

    def register_effect(self, e: Effect, buff_eff=False, out=True):
        """

        :param e:
        :param buff_eff: 是否是附加的效果。
        :param out: 是否输出
        :return:
        """
        self.effects.append(e)
        if buff_eff:
            self.buff_eff[e] = e.description
            # 通知双方
            if out:
                for p in self.game.players:
                    if (p is self.game.get_player(self)) | (self.cover == 0):
                        p.update_vc(self)
                    else:
                        p.update_vc_ano(self)
        if e.act_phase == self.game.phase_now and e.trigger:
            self.game.ef_listener.append(e)

    def remove_effect(self, e, out=True):
        if e in self.effects:
            self.effects.remove(e)
            if e in self.buff_eff:
                self.buff_eff.pop(e)
                # 通知双方
                if out:
                    for p in self.game.players:
                        if (p is self.game.get_player(self)) | (self.cover == 0):
                            p.update_vc(self)
                        else:
                            p.update_vc_ano(self)
            if e in self.game.ef_listener:
                e.removing = True

    def remove_buff(self, op, v):
        self.ATK.remove(op, v)
        self.DEF.remove(op, v)

    def reset(self):
        """
        离场时，清除所有非永久的buff，效果复原。
        :return:
        """
        i = 0
        while i < len(self.effects):
            if not self.effects[i].no_reset:
                self.remove_effect(self.effects[i])  # , False)
            else:
                i += 1
        if self.cid is not None:
            m = import_module('cards.c{}'.format(self.cid))
            m.give(self)
        self.attack_times = 0
        self.block_times = 0
        self.posture_times = 0
        self.ATK.reset()
        self.DEF.reset()
        self.turns = 0
        self.sign = dict()

    def hp_cost(self, v, ef: Effect = None):
        """
        尝试支付生命力。策略则改为支付EFF。
        :param v:
        :param ef:
        :return:
        """
        tp = TimePoint(ETimePoint.TRY_HP_COST, ef, [self, v, 1])
        self.game.enter_time_point(tp)
        p = self.ATK.value if self.type == ECardType.STRATEGY else self.DEF.value
        if tp.args[-1] & (p > tp.args[1]):
            yield True
            tp = TimePoint(ETimePoint.HP_COSTING, ef, [self, v, 1])
            self.game.enter_time_point(tp)
            if tp.args[-1]:
                # 代支付
                c, v = tp.args[:-1]
                if c.type == ECardType.STRATEGY:
                    c.ATK.gain(-v, False, ef)
                else:
                    c.DEF.gain(-v, False, ef)
                # 通知玩家
                c.game.batch_sending('hp_cst', [c.vid, v])
                c.game.enter_time_point(TimePoint(ETimePoint.HP_COST, ef, [c.vid, v]))
        yield False

    def attack(self, target, block=False):
        """
        直接攻击。
        :param target:
        :param block:
        :return:
        """
        if target.type == ECardType.LEADER:
            self.game.deal_damage(self, target, self.ATK.value, None)
        else:
            damage = self.ATK.value - target.DEF.value if block else 0
            tp = TimePoint(ETimePoint.ATTACK_DAMAGE_JUDGE, None, [self, target, damage])
            self.game.enter_time_point(tp)
            if tp.args[2] > 0:
                self.game.deal_damage(self, self.game.get_player(target).leader, tp.args[2])
            f = 0
            if target.posture:
                if self.ATK.value > target.DEF.value:
                    f = 1
                elif self.ATK.value < target.DEF.value:
                    f = 2
            elif block:
                if self.ATK.value > target.DEF.value:
                    f = 1
                elif self.ATK.value < target.DEF.value:
                    f = 2
                self.game.temp_tp_stack.append(TimePoint(ETimePoint.BLOCKED, None, [self, target]))
            else:
                if self.ATK.value > target.ATK.value:
                    f = 1
                elif self.ATK.value < target.ATK.value:
                    f = 2
                elif self.ATK.value == target.ATK.value:
                    f = 3

            self.game.enter_time_point(TimePoint(ETimePoint.ATTACK_COMPLETE, None, [self, target]))

            if f == 1:
                self.game.destroy(self, target)
            elif f == 2:
                self.game.destroy(target, self)
            elif f == 3:
                self.game.destroy(self, target)
                self.game.destroy(target, self)
        self.game.temp_tp_stack.append(TimePoint(ETimePoint.ATTACKED, None, [self, target]))
        self.game.enter_time_points()

    def reset_times(self):
        self.attack_times = 1
        self.block_times = 1
        if (self.game.turn_phase == ETurnPhase.BEGINNING) & (self.turns > 1):
            self.posture_times = 1
        self.game.enter_time_point(TimePoint(ETimePoint.RESET_TIMES, None, self))

    def move_to(self, ef, loc, ind=-1):
        """
        移动至另一个区域。不能单独使用(但移动区域时必须调用)，不会触发时点。
        :param ef: effect
        :param loc:
        :param ind: 插入位置
        :return:
        """
        if loc != self.location:
            p = self.game.players[(self.location & ELocation.P1) == 0]
            pt = self.game.players[(loc & ELocation.P1) == 0]

            def leave():
                if self.location & ELocation.HAND:
                    return ETimePoint.OUT_HAND, ETimePoint.OUT_HAND_END, p.hand
                if self.location & ELocation.DECK:
                    return ETimePoint.OUT_DECK, ETimePoint.OUT_DECK_END, p.deck
                if self.location & ELocation.SIDE:
                    return ETimePoint.OUT_SIDE, ETimePoint.OUT_SIDE_END, p.side
                if self.location & ELocation.ON_FIELD:
                    return ETimePoint.OUT_FIELD, ETimePoint.OUT_FIELD_END, p.on_field
                if self.location & ELocation.GRAVE:
                    return ETimePoint.OUT_GRAVE, ETimePoint.OUT_GRAVE_END, p.grave
                if self.location & ELocation.EXILED:
                    return ETimePoint.OUT_EXILED, ETimePoint.OUT_EXILED_END, p.exiled
                return None, None, None

            def enter():
                if loc & ELocation.HAND:
                    return ETimePoint.IN_HAND, ETimePoint.IN_HAND_END, pt.hand
                if loc & ELocation.DECK:
                    return ETimePoint.IN_DECK, ETimePoint.IN_DECK_END, pt.deck
                if loc & ELocation.SIDE:
                    return ETimePoint.IN_SIDE, ETimePoint.IN_SIDE_END, pt.side
                if loc & ELocation.ON_FIELD:
                    return ETimePoint.IN_FIELD, ETimePoint.IN_FIELD_END, pt.on_field
                if loc & ELocation.GRAVE:
                    return ETimePoint.IN_GRAVE, ETimePoint.IN_GRAVE_END, pt.grave
                if loc & ELocation.EXILED:
                    return ETimePoint.IN_EXILED, ETimePoint.IN_EXILED_END, pt.exiled

            # 离开我方半场去到对方半场不算离场
            etp1, etp3, _from = leave()
            etp2, etp4, _to = enter()
            f = True
            if etp1:
                tp1 = TimePoint(etp1, ef, [self, self.location, 1])
                self.game.temp_tp_stack.append(tp1)
                f = tp1.args[-1]
            tp2 = TimePoint(etp2, ef, [self, loc, 1])
            self.game.temp_tp_stack.append(tp2)
            yield True
            yield f & tp2.args[-1]
            # 离开, 离场需特殊处理，不能直接remove
            if self.location & ELocation.ON_FIELD:
                p.on_field[self.inf_pos] = None
            elif _from:
                _from.remove(self)
            # 进入, 入场的具体位置不在这里处理
            pre_loc = self.location
            self.location = loc
            if ind > -1:
                if (loc & ELocation.ON_FIELD) > 0:
                    _to[ind] = self
                else:
                    _to.insert(ind, self)
            elif (loc & ELocation.ON_FIELD) == 0:
                _to.append(self)
            if etp3:
                if (etp3 == ETimePoint.OUT_FIELD_END) & (etp2 != ETimePoint.IN_FIELD):
                    self.reset()
                tp3 = TimePoint(etp3, ef, [self, pre_loc])
                self.game.temp_tp_stack.append(tp3)
            if (etp4 == ETimePoint.IN_HAND_END) | (etp4 == ETimePoint.IN_DECK_END) | \
                    (etp4 == ETimePoint.IN_SIDE_END):
                self.turns = 0
                self.cover = 1
            elif etp4 == ETimePoint.IN_GRAVE_END:
                self.turns = 0
                self.cover = 0
            elif etp4 == ETimePoint.IN_FIELD_END:
                self.game.skip_times = 0
            else:
                self.turns = 0
            tp4 = TimePoint(etp4, ef, [self, loc, pre_loc])
            self.game.temp_tp_stack.append(tp4)
            yield True
        else:
            yield False
            yield True
            yield True

    def serialize(self):
        return {
            'vid': self.vid,
            'cid': self.cid,
            'name': self.name,
            'type': self.type,
            'subtype': self.subtype,
            'rank': self.rank,
            'series': self.series,
            'src_atk': self.src_atk,
            'src_def': self.src_def,
            'add_val': self.ATK.add_val,
            'atk': self.ATK.value,
            'def': self.DEF.value,
            'is_token': self.is_token,
            'location': self.location,
            'buff_eff': list(self.buff_eff.values()),
            'inf_pos': self.inf_pos,
            'posture': int(self.posture),
            'cover': self.cover,
            'sign': self.sign,
                           }

    def serialize_anonymous(self):
        return {
            'vid': self.vid,
            'add_val': self.ATK.add_val,
            'location': self.location,
            'buff_eff': list(self.buff_eff.values()),
            'inf_pos': self.inf_pos,
            'posture': int(self.posture),
            'cover': self.cover,
            'sign': self.sign,
                           }


class GCIDManager:
    def __init__(self):
        # {gcid: GameCard, ...}
        self.cards = dict()

    def register(self, c: GameCard):
        gcid = randint(0, 99999999)
        while gcid in self.cards.keys():
            gcid = randint(0, 99999999)
        self.cards[gcid] = c
        c.vid = gcid

    def change(self, gcid):
        c = self.cards.pop(gcid)
        new_gcid = randint(0, 99999999)
        while new_gcid in self.cards.keys():
            new_gcid = randint(0, 99999999)
        c.vid = new_gcid
        self.cards[new_gcid] = c

    def recycle(self, gcid: int):
        self.cards.pop(gcid)

    def get_card(self, gcid: int):
        return self.cards[gcid]

    def get_cards(self):
        return self.cards.values()


class TimePoint:
    def __init__(self, tp_id, sender: Effect = None, args=None):
        self.tp = tp_id
        self.sender = sender
        self.args = args

    @staticmethod
    def generate(tp_id):
        return TimePoint(tp_id)


class Match:
    """
    一次比赛（三局两胜）。
    """
    def __init__(self, p1: Player, p1deck, p1leader_id,
                 p2: Player, p2deck, p2leader_id, match_config):
        """

        :param p1: 玩家1
        :param p1deck: 玩家1的主卡组&备选卡组
        :param p1leader_id: 玩家1的领袖卡ID
        :param p2:
        :param p2deck:
        :param p2leader_id:
        :param match_config: 比赛的额外配置
        """
        gp1 = GamePlayer(p1, p1deck, p1leader_id)
        gp2 = GamePlayer(p2, p2deck, p2leader_id)
        self.players = [gp1, gp2]
        self.match_config = match_config
        self.game = None

        self.wins = {gp1: 0, gp2: 0}

    def start(self):
        self.batch_sending('startm')
        exec(self.match_config["match_init"])
        last_loser = None
        while True:
            self.game = Game(self.players, self.match_config["game_config"], last_loser)
            pl: tuple = self.game.start()
            self.wins[pl[0]] += 1
            last_loser = pl[1]
            self.batch_sending('endg', [self.game.win_reason], pl[0])
            winner: GamePlayer = self.end_check()
            if winner is not None:
                self.batch_sending('endm', None, winner)
                exec(self.match_config['match_end'])
                return winner
            self.batch_sending('mbreak')
            exec(self.match_config['match_break'])

    def end_check(self):
        """
        比赛是否结束。
        :return: 比赛胜者。
        """
        for p in self.players:
            if self.wins[p] >= self.match_config['wins_need']:
                return p
        return None

    def batch_sending(self, op, args: list = None, sender=None):
        """
        群发消息。
        :return:
        """
        for p in self.players:
            p.output(op, args, True if sender is None else p is sender)


class Game:
    """
    一个单局对局。特殊规则可由领袖卡的隐藏效果引入。
    """

    def __init__(self, players: list, game_config, last_loser: GamePlayer):
        self.tp_stack = list()
        # 事件栈帧，用来记录/保存对局，
        # 以及辅助实现一些卡的向前查询功能(比如人文主义者的：上回合我方进行过阻挡时...)。
        self.event_stack = list()
        # 临时时点调用栈，每个时点都询问一次对玩家打扰率比较高，所以可以合并一些时点的处理。
        self.temp_tp_stack = list()
        # 先手的索引为0
        self.players = players
        # 先手玩家代表
        self.p1: GamePlayer = None
        # 后手玩家代表
        self.p2: GamePlayer = None
        # 进行当前回合的玩家代表
        self.turn_player: GamePlayer = None
        # 未进行当前回合的玩家代表
        self.op_player: GamePlayer = None

        # 当前回合数
        self.turns = 0
        self.turn_phase = None
        self.game_config = game_config
        # 棋盘规模。
        self.scale = self.game_config['scale']
        # 放置&取走阶段时用的6*6棋盘
        self.chessboard = [None for x in range(0, self.scale ** 2)]
        self.last_loser = last_loser
        self.phase_now = None
        self.winner: GamePlayer = None
        self.win_reason = 0
        self.start_time = datetime.now()
        self.loser: GamePlayer = None
        # 连锁计数。
        self.react_times = 0
        # 连续跳过(np)次数，进入/离开场地才会重置计数。
        self.skip_times = 0
        # 连续跳过次数达到该值时立即进行单局胜负判定。
        self.max_skip = self.game_config['max_skip']
        self.turn_process = self.game_config['turn_process']
        self.time_limit = self.game_config.get('time_limit', None)
        # 在当前阶段所有需要检查是否满足了触发条件的效果
        self.ef_listener = list()
        self.vid_manager = GCIDManager()

    def start(self):
        """
        双方都已准备好。开始进行游戏。
        :return: 列表，前者为获胜的玩家代表，后者为落败的玩家代表。
        """
        # sp: starting player
        # 游戏流程
        for p in self.players:
            p.output('startg')

        # t1 = Thread(None, self.check_winner)
        # t1.setDaemon(True)
        # t1.start()
        # if self.time_limit:
        #     t1.join(self.time_limit)
        # else:
        # t1.join()
        self.check_winner()
        if self.winner is None:
            self.win_reason = 4
            self.judge()
            self.loser = self.players[self.winner.sp]
        return self.winner, self.loser

    def check_winner(self):
        # t2 = Thread(None, self.run_process)
        # t2.setDaemon(True)
        # t2.start()
        # while self.winner is None:
        #     sleep(1)
        process = self.game_config['process']
        for ph in process:
            self.enter_phase(ph)
            if self.winner is not None:
                break
        self.loser = self.players[self.winner.sp]

    def run_process(self):
        process = self.game_config['process']
        for ph in process:
            self.enter_phase(ph)

    def enter_phase(self, ph):
        self.phase_now = ph
        self.update_ef_list()
        if ph == EGamePhase.SP_DECIDE:
            self.__ph_sp_decide()
            self.__end_phase(ETimePoint.PH_SP_DECIDE_END)
        elif ph == EGamePhase.INITIALIZE:
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_GAME_START), False)
        elif ph == EGamePhase.SHOW_CARD:
            self.__enter_phase(ETimePoint.PH_SHOWED_CARD)
            self.__ph_show_card()
            self.__end_phase(ETimePoint.PH_SHOWED_CARD_END)
        elif ph == EGamePhase.EXTRA_DATA:
            self.__enter_phase(ETimePoint.PH_EXTRA_DATA)
            self.__ph_extra_data()
            self.__end_phase(ETimePoint.PH_EXTRA_DATA_END)
        elif ph == EGamePhase.PUT_CARD:
            self.__enter_phase(ETimePoint.PH_PUT_CARD)
            self.__ph_put_card()
            self.__end_phase(ETimePoint.PH_PUT_CARD_END)
        elif ph == EGamePhase.TAKE_CARD:
            self.__enter_phase(ETimePoint.PH_TAKE_CARD)
            self.__ph_take_card()
            self.__end_phase(ETimePoint.PH_TAKE_CARD_END)
        elif ph == EGamePhase.MULLIGAN:
            self.__enter_phase(ETimePoint.PH_MULLIGAN)
            self.__ph_mulligan()
            self.__end_phase(ETimePoint.PH_MULLIGAN_END)
        elif ph == EGamePhase.PLAY_CARD:
            self.__enter_phase(ETimePoint.PH_PLAY_CARD)
            self.__ph_play_card()
        elif ph == EGamePhase.RANDOM_PUT:
            self.__enter_phase(ETimePoint.PH_RANDOM_PUT)
            self.__ph_random_put()
            self.__end_phase(ETimePoint.PH_RANDOM_PUT_END)

    def __enter_phase(self, tp):
        self.enter_time_point(TimePoint.generate(tp), False)
        self.batch_sending('ent_ph', [self.phase_now])

    def __end_phase(self, tp):
        self.enter_time_point(TimePoint.generate(tp), False)
        self.batch_sending('endp', [tp])

    def __ph_sp_decide(self):
        a = randint(1, 16)
        if a > 8:
            self.p1 = self.players[0]
            self.p2 = self.players[1]
        else:
            self.p1 = self.players[1]
            self.p2 = self.players[0]
            self.players[0] = self.p1
            self.players[1] = self.p2
        # 输出
        self.batch_sending('sp_decided', None, self.p1)

        self.turn_player = self.p1
        self.op_player = self.p2

        self.p1.init_game(self)
        self.p2.init_game(self)

        self.p1.init_card_info()
        self.p2.init_card_info()

    def __ph_show_card(self):
        def show_one(p: GamePlayer, rank):
            def check_ind(ind):
                return 0 if ind in range(0, ind_max) else EErrorCode.OVERSTEP

            p.output('req_shw_crd', [rank])

            card_vid = [c.vid for c in p.hand if c.rank == rank]
            ind_max = len(card_vid)
            shown_card_index = p.input(check_ind, 'req_chs_tgt',
                                       [card_vid, 1, 1])

            self.show_card(p, card_vid[shown_card_index])

        show_one(self.p1, ECardRank.TRUMP)
        show_one(self.p2, ECardRank.TRUMP)
        show_one(self.p1, ECardRank.GOOD)
        show_one(self.p2, ECardRank.GOOD)
        show_one(self.p1, ECardRank.COMMON)
        show_one(self.p2, ECardRank.COMMON)
        self.p1.shuffle()
        self.p2.shuffle()

    def __ph_extra_data(self):
        def gen(p: GamePlayer):
            nums = [-1000, -500, 500, 1000, -1000, -500, 500, 1000]
            for i in range(8, 18):
                nums.append(randint(-2, 2) * 500)
            for i in range(0, 18):
                p.hand[i].ATK.add_val = nums[i]
                self.enter_time_point(TimePoint(ETimePoint.EXTRA_DATA_GENERATING, None, p.hand[i]))
                p.update_vc(p.hand[i])
            # 调查筹码
            f = 1
            i = 0
            while f >= 1:
                i = randint(0, len(p.hand) - 1)
                if p.hand[i].rank == ECardRank.TRUMP:
                    f = randint(0, 2)
                else:
                    break
            p.hand[i].ATK.add_val = 0
            p.hand[i].register_effect(EffInvestigator(p.hand[i]), True)
            p.hand[i].can_random_put = False
            p.update_vc(p.hand[i])
            self.enter_time_point(TimePoint(ETimePoint.INVESTIGATOR_GENERATED, None, p.hand[i]))

        gen(self.p1)
        gen(self.p2)

        self.enter_time_point(TimePoint(ETimePoint.EXTRA_DATA_GENERATED))
        # 用处是传输。
        self.p1.shuffle()
        self.p2.shuffle()

        self.batch_sending('lst_all_ano')

    def __ph_random_put(self):
        extra = [-500, -500, 0, 500]
        exclude = {-12: [-7, -5], -5: [-12, -7, 2, 7], 2: [7, -5], 7: [-5, 2, 5, 12],
                   +12: [7, 5], 5: [12, 7, -2, -7], -2: [-7, 5], -7: [5, -2, -5, -12]}
        p1pos = [x for x in range(0, self.scale ** 2)]
        p2pos = [x for x in range(0, self.scale ** 2)]

        def put(p, ppos):
            while True:
                c = p.hand[randint(0, len(p.hand) - 1)]
                if c.can_random_put:
                    # 王牌随机放置的概率减半
                    if c.rank == ECardRank.TRUMP:
                        if randint(0, 2) < 2:
                            continue
                    break
            pos = ppos[randint(0, len(ppos) - 1)]
            self.chessboard[pos] = c
            p.hand.remove(c)
            self.batch_sending('rnd_put', [pos, c.vid], p)
            c.ATK.change_adv(extra[randint(0, 3)])
            if pos in p1pos:
                p1pos.remove(pos)
            if pos in p2pos:
                p2pos.remove(pos)
            for k in exclude.keys():
                if (pos + k) in range(0, self.scale ** 2):
                    if self.chessboard[pos + k] is not None:
                        if (self.chessboard[pos + k].location & (2 - p.sp)) > 0:
                            for ex in exclude[k]:
                                if (pos + ex) in ppos:
                                    ppos.remove(pos + ex)

        for i in range(0, 6):
            put(self.p1, p1pos)
            put(self.p2, p2pos)

    def __ph_put_card(self):
        # 落子
        def go(p: GamePlayer):
            # 检查落子合法性
            def check_go(_x, _y, _ind):
                if (_y * self.scale + _x not in range(0, self.scale ** 2)) | (_ind not in range(0, ind_max)):
                    return EErrorCode.OVERSTEP
                return 0 if self.chessboard[_y * self.scale + _x] is None \
                    else EErrorCode.INVALID_PUT

            hand = p.hand
            if len(hand) == 0:
                return False
            else:
                ind_max = len(hand)
                # x, y, ind
                x, y, ind = p.input(check_go, 'req_go')
                card = hand[ind]
                self.chessboard[y * self.scale + x] = card
                hand.remove(card)
                # 变化周围的数值。
                cs = adj_pos(x, y, self.scale)
                for ac in cs:
                    if self.chessboard[ac] is not None:
                        self.chessboard[ac].ATK.add_val += card.ATK.add_val
                        self.chessboard[ac].ATK.update()
                self.batch_sending('go', [x, y, card.vid], p)
                # 影响力值发挥作用后归零，成为附加值。
                card.ATK.add_val = 0
                card.ATK.update()

                # 放下后的处理。
                self.enter_time_point(TimePoint(ETimePoint.CARD_PUT, None, [x, y, card]))
                return True
        f = True
        while f:
            f = go(self.p2) | go(self.p1)
        self.enter_time_point(TimePoint(ETimePoint.EXTRA_DATA_CALC))
        # 结算附加值。
        for c in self.chessboard:
            c.ATK.update()

    def __ph_take_card(self):
        def take_card(p: GamePlayer):
            # direction: 0: 只取走1个筹码 6: 同时取走下方的筹码 1: 同时取走右侧的筹码
            def check(_x, _y, direction):
                if (direction != self.scale) & (direction != 1) & (direction != 0):
                    return EErrorCode.INVALID_TOOK
                if (_x == 5) & (direction == 1):
                    return EErrorCode.INVALID_TOOK
                if (_y == 5) & (direction == 6):
                    return EErrorCode.INVALID_TOOK
                if (self.chessboard[self.scale * _y + _x] is None) | \
                        (self.scale * _y + _x + direction not in range(0, self.scale ** 2)):
                    return EErrorCode.DONT_EXIST
                return 0 if self.chessboard[self.scale * _y + _x + direction] is not None\
                    else EErrorCode.DONT_EXIST
            x, y, d = p.input(check, 'req_tk_crd')
            # 将卡取走。最多只能取到一半的卡
            if d != 0 and len(p.hand) < self.scale ** 2 / 2 - 1:
                cards = [self.scale * y + x, self.scale * y + x + d]
            else:
                cards = [self.scale * y + x]
            for pos in cards:
                card = self.chessboard[pos]
                self.chessboard[pos] = None
                p.hand.append(card)
                card.location = 2 - p.sp + ELocation.HAND
                p.update_vc(card)
                self.batch_sending('tk_crd', [pos, 0], p)
                self.enter_time_point(TimePoint(ETimePoint.CARD_TOOK, None, [card, len(cards)]))

        f = True
        while f:
            f = False

            if len(self.turn_player.hand) < self.scale ** 2 / 2:
                take_card(self.turn_player)
            self.exchange_turn()

            for c in self.chessboard:
                f = f | (c is not None)
        self.turn_player.shuffle()
        self.op_player.shuffle()

    def __ph_mulligan(self):
        """
        调整阶段。
        :return:
        """
        def check_exchange(_m, _s):
            """
            检查手牌中序号_m的卡是否能交换副卡组中序号_s的卡
            :param _m:
            :param _s:
            :return:
            """
            if (_m in range(0, len(pn.hand))) & (_s in range(0, len(pn.side))):
                # 王牌补偿，满足条件时，任意筹码都可以交换副卡组中的王牌筹码
                if pn.side[_s].rank == ECardRank.TRUMP:
                    return True
                return pn.hand[_m].rank >= pn.side[_s].rank
            else:
                return True

        def check(_m1, _m2, _s1, _s2):
            """
            :param _m1:
            :param _m2:
            :param _s1:
            :param _s2:
            :return:
            """
            _tc = 0
            _tcs = 0
            for _c in pn.hand:
                if _c.rank == ECardRank.TRUMP:
                    _tc += 1
            if _s1 in range(0, len(pn.side)):
                if pn.side[_s1].rank == ECardRank.TRUMP:
                    _tcs += 1
            if _s2 in range(0, len(pn.side)):
                # 连续交换副卡组中同一位置的牌。
                if _s2 == _s1:
                    if pn.hand[_m1].rank == ECardRank.TRUMP:
                        _tcs += 1
                else:
                    if pn.side[_s2].rank == ECardRank.TRUMP:
                        _tcs += 1
            if (_tc + _tcs > 3) & (_tcs > 0):
                return EErrorCode.NO_MORE_TRUMP
            if check_exchange(_m1, _s1) & check_exchange(_m2, _s2):
                return 0
            elif check_exchange(_m1, _s2) & check_exchange(_m2, _s1):
                return 0
            return EErrorCode.FORBIDDEN_EXCHANGE

        # 收到进入调整阶段的消息时客户端即可进行操作。mul指令只是用于回收用户发来的指令。
        for p in self.players:
            pn = p
            r = p.free_input(check, 'req_mul')
            if r is not None:
                m1, m2, s1, s2 = r
                if (m1 in range(0, len(p.hand))) & (s1 in range(0, len(p.side))):
                    t = p.hand[m1]
                    p.hand[m1] = p.side[s1]
                    p.hand[m1].location = ELocation.HAND + 2 - p.sp
                    t.location = ELocation.SIDE + 2 - p.sp
                    p.side[s1] = t
                    p.update_vc(p.hand[m1])
                    p.update_vc(t)
                if (m2 in range(0, len(p.hand))) & (s2 in range(0, len(p.side))):
                    t = p.hand[m2]
                    p.hand[m2] = p.side[s2]
                    p.hand[m2].location = ELocation.HAND + 2 - p.sp
                    t.location = ELocation.SIDE + 2 - p.sp
                    p.side[s2] = t
                    p.update_vc(p.hand[m2])
                    p.update_vc(t)
                p.shuffle()

    def __ph_play_card(self):
        def check(*_args):
            if len(_args) == 1:
                return EErrorCode.INVALID_INPUT
            # play card 打出手牌
            if _args[0] == 0:
                # 只能在主要阶段打出手牌。
                if (self.turn_phase != ETurnPhase.M1) & (self.turn_phase != ETurnPhase.M2):
                    return EErrorCode.WRONG_PHASE
                if _args[1] not in range(0, len(self.turn_player.hand)):
                    return EErrorCode.OVERSTEP
                _c = self.turn_player.hand[_args[1]]
                if _c.type == ECardType.EMPLOYEE:
                    # 不在雇员区域或该区域已有雇员
                    if _args[2] not in range(0, 3):
                        return EErrorCode.OVERSTEP
                    if self.turn_player.on_field[_args[2]] is not None:
                        return EErrorCode.INVALID_PUT
                    _tp = TimePoint(ETimePoint.TRY_SUMMON, None, [_c, self.turn_player, _args[2], _args[3], 1])
                    self.enter_time_point(_tp)
                    # 换掉_c的效果不会出，太奇怪了
                    if not _tp.args[-1]:
                        return EErrorCode.FORBIDDEN_SUMMON
                    # 是否还有剩余的入场次数
                    if self.turn_player.summon_times == 0:
                        return EErrorCode.TIMES_LIMIT
                    _tp = TimePoint(ETimePoint.TRIED_SUMMON, None, [_c, self.turn_player, _args[2], _args[3],
                                                                    _tp.args[-1]])
                    self.enter_time_point(_tp)
                    return 0
                elif _c.type == ECardType.STRATEGY:
                    # 不在策略区域或该区域已有策略
                    if _args[2] not in range(3, 6):
                        return EErrorCode.OVERSTEP
                    if self.turn_player.on_field[_args[2]] is not None:
                        return EErrorCode.INVALID_PUT
                    # 反制策略无法直接发动(除非 不败律师 的效果适用中)
                    if _c.subtype & EStrategyType.COUNTER:
                        return EErrorCode.PLAY_COUNTER
                    # 其他种类的策略发动时会顺带发动效果
                    _tp1 = TimePoint(ETimePoint.TRY_ACTIVATE_STRATEGY, None, [_c, 1])
                    _tp2 = TimePoint(ETimePoint.TRY_ACTIVATE_EFFECT, None, [_c.effects[0], 1])
                    self.temp_tp_stack.append(_tp1)
                    self.temp_tp_stack.append(_tp2)
                    self.enter_time_points()
                    if not(_tp1.args[-1] & _tp2.args[-1] & _c.effects[0].condition(None)):
                        self.enter_time_point(TimePoint(ETimePoint.TRIED_ACTIVATE_STRATEGY, None,
                                                        [_c, _tp1.args[-1]]))
                        return EErrorCode.FORBIDDEN_STRATEGY
                    self.enter_time_point(TimePoint(ETimePoint.TRIED_ACTIVATE_STRATEGY, None,
                                                    [_c, _tp1.args[-1]]))
                    # 是否还有剩余的使用次数
                    if (self.turn_player.strategy_times == 0) & (self.turn_player.activate_times == 0):
                        return EErrorCode.TIMES_LIMIT
                    return 0
                return EErrorCode.UNKNOWN_CARD
            # act 询问可发动的效果
            elif _args[0] == 1:
                if (self.turn_phase != ETurnPhase.M1) & (self.turn_phase != ETurnPhase.M2):
                    return EErrorCode.WRONG_PHASE
                return 0
            # set 将手牌盖放到场上
            elif _args[0] == 2:
                # 只能在主要阶段打出手牌。
                if (self.turn_phase != ETurnPhase.M1) & (self.turn_phase != ETurnPhase.M2):
                    return EErrorCode.WRONG_PHASE
                if _args[1] not in range(0, len(self.turn_player.hand)):
                    return EErrorCode.OVERSTEP
                _c = self.turn_player.hand[_args[1]]
                if _c.type == ECardType.EMPLOYEE:
                    # 非秘密雇员不能盖放。
                    if (_c.subtype & EEmployeeType.SECRET) == 0:
                        return EErrorCode.CANNOT_SET
                    # 不在雇员区域或该区域已有雇员
                    if _args[2] not in range(0, 3):
                        return EErrorCode.OVERSTEP
                    if self.turn_player.on_field[_args[2]] is not None:
                        return EErrorCode.INVALID_PUT
                    _tp = TimePoint(ETimePoint.TRY_SET_EM, None, [_c, 1])
                    self.enter_time_point(_tp)
                    if not _tp.args[-1]:
                        return EErrorCode.FORBIDDEN_SET
                    # 是否还有剩余的入场次数
                    if self.turn_player.summon_times == 0:
                        return EErrorCode.TIMES_LIMIT
                    return 0
                elif _c.type == ECardType.STRATEGY:
                    # 不在策略区域或该区域已有策略
                    if _args[2] not in range(3, 6):
                        return EErrorCode.OVERSTEP
                    if self.turn_player.on_field[_args[2]] is not None:
                        return EErrorCode.INVALID_PUT
                    _tp = TimePoint(ETimePoint.TRY_SET_STRATEGY, None, [_c, 1])
                    self.enter_time_point(_tp)
                    if not _tp.args[-1]:
                        return EErrorCode.FORBIDDEN_SET
                    # 是否还有剩余的使用次数
                    if (self.turn_player.strategy_times == 0) & (self.turn_player.set_times == 0):
                        return EErrorCode.TIMES_LIMIT
                    return 0
                return EErrorCode.UNKNOWN_CARD
            # attack/quick attack 尝试发动攻击
            elif (_args[0] == 3) | (_args[0] == 7):
                # 只能在战斗阶段发动攻击。
                if (self.turn_phase != ETurnPhase.BP1) & (self.turn_phase != ETurnPhase.LBP1) &\
                        (self.turn_phase != ETurnPhase.LBP2):
                    return EErrorCode.WRONG_PHASE
                if _args[1] not in range(0, 3):
                    return EErrorCode.OVERSTEP
                _c = self.turn_player.on_field[_args[1]]
                if _c is None:
                    return EErrorCode.DONT_EXIST
                # 防御姿态不能攻击。
                if _c.posture:
                    return EErrorCode.DEFEND_POSTURE
                # 为负数可以无限攻击。
                if _c.attack_times == 0:
                    return EErrorCode.TIMES_LIMIT
                _tp = TimePoint(ETimePoint.TRY_ATTACK_ANNOUNCE, None, [_c, 1])
                self.enter_time_point(_tp)
                if not _tp.args[-1]:
                    return EErrorCode.FORBIDDEN_ATTACK
                if _args[0] == 7:
                    # 模拟攻击以筛选可攻击目标
                    _atk_tgt = list()
                    for _em in self.op_player.on_field:
                        if _em is not None and _em.type == ECardType.EMPLOYEE:
                            _tp = TimePoint(ETimePoint.TRY_ATTACK, None, [_c, _em, 1])
                            self.enter_time_point(_tp)
                            if _tp.args[-1]:
                                _atk_tgt.append(_em.vid)
                    _tp = TimePoint(ETimePoint.TRY_ATTACK, None, [_c, self.op_player.leader, 1])
                    self.enter_time_point(_tp)
                    # 入场回合默认不能直接攻击对方领袖。
                    # 风行检查
                    self.enter_time_point(TimePoint(ETimePoint.CHARGE_CHECK, None, _c))
                    if _tp.args[-1] & ((_c.charge | _c.turns) > 0):
                        _atk_tgt.append(self.op_player.leader.vid)
                        _c.charge = False
                    if _args[2] not in _atk_tgt:
                        return EErrorCode.FORBIDDEN_ATTACK
                return 0
            # next phase 主动进行自己回合的下个阶段
            elif _args[0] == 4:
                return 0
            # good game 单局认输
            elif _args[0] == 5:
                return 0
            # change posture 转变姿态
            elif _args[0] == 6:
                # 主要阶段内才能转变姿态。
                if (self.turn_phase != ETurnPhase.M1) & (self.turn_phase != ETurnPhase.M2):
                    return EErrorCode.WRONG_PHASE
                # 雇员
                if _args[1] in range(0, 3):
                    _c = self.turn_player.on_field[_args[1]]
                    if _c is None:
                        return EErrorCode.DONT_EXIST
                    if _c.cover == 1:
                        _tp = TimePoint(ETimePoint.TRY_UNCOVER_EM, None, [c, 1])
                        self.enter_time_point(_tp)
                        if not _tp.args[-1]:
                            return EErrorCode.FORBIDDEN_UNCOVER
                    else:
                        # 有剩余的攻击次数才能作姿态转换。
                        if _c.attack_times == 0:
                            return EErrorCode.NO_TIMES_REMAIN
                        # 还有剩余的转换次数，为负数可以无限次数转换
                        if _c.posture_times == 0:
                            return EErrorCode.TIMES_LIMIT
                        _tp = TimePoint(ETimePoint.TRY_CHANGE_POSTURE, None, [_c, 1])
                        self.enter_time_point(_tp)
                        if _tp.args[-1] == 0:
                            return EErrorCode.FORBIDDEN_CP
                    return 0
                # 策略
                elif _args[1] in range(3, 6):
                    _c = self.turn_player.on_field[_args[1]]
                    if _c is None:
                        return EErrorCode.DONT_EXIST
                    if _c.cover == 1:
                        # 反制策略不能直接发动。
                        if _c.subtype & EStrategyType.COUNTER:
                            return EErrorCode.PLAY_COUNTER
                        _tp0 = TimePoint(ETimePoint.TRY_UNCOVER_STRATEGY, None, [_c, 1])
                        _tp1 = TimePoint(ETimePoint.TRY_ACTIVATE_STRATEGY, None, [_c, 1])
                        _tp2 = TimePoint(ETimePoint.TRY_ACTIVATE_EFFECT, None, [_c.effects[0], 1])
                        self.temp_tp_stack.append(_tp0)
                        self.temp_tp_stack.append(_tp1)
                        self.temp_tp_stack.append(_tp2)
                        self.enter_time_points()
                        if not (_tp0.args[-1] & _tp1.args[-1] & _tp2.args[-1] & _c.effects[0].condition(None)):
                            self.enter_time_point(TimePoint(ETimePoint.TRIED_ACTIVATE_STRATEGY, None,
                                                            [_c, _tp1.args[-1]]))
                            return EErrorCode.FORBIDDEN_STRATEGY
                        self.enter_time_point(TimePoint(ETimePoint.TRIED_ACTIVATE_STRATEGY, None,
                                                        [_c, _tp1.args[-1]]))
                        return 0
                    return EErrorCode.ALREADY_UNCOVERED
                else:
                    return EErrorCode.OVERSTEP
            # end turn 主动结束回合
            elif _args[0] == 8:
                return 0
            else:
                return EErrorCode.INVALID_INPUT

        def check_ind(_ind):
            if _ind not in range(0, _len):
                return EErrorCode.OVERSTEP
            return 0

        # 重置先后手
        self.turn_player = self.p1
        self.op_player = self.p2
        while self.winner is None:
            if self.turns >= 50:
                self.win_reason = 3
                self.judge()
                break
            ntp = self.next_turn_phase()
            self.next_turn(ntp)
            while (self.turn_phase != ETurnPhase.ENDING) & (self.winner is None):
                cmd = self.turn_player.input(check, 'req_op')
                # play card 打出手牌
                if cmd[0] == 0:
                    c = self.turn_player.hand[cmd[1]]
                    # 先消耗次数。
                    if c.type == ECardType.EMPLOYEE:
                        self.turn_player.summon_times -= 1
                        self.summon(self.turn_player, self.turn_player, c, cmd[2], cmd[3])
                    elif c.type == ECardType.STRATEGY:
                        if self.turn_player.activate_times:
                            self.turn_player.activate_times -= 1
                        else:
                            self.turn_player.strategy_times -= 1
                        self.activate_strategy(self.turn_player, self.turn_player, c, cmd[2])
                # act 询问可发动的效果
                elif cmd[0] == 1:
                    efs = list()
                    for c in self.vid_manager.get_cards():
                        # 场上盖放的策略不在这里处理
                        if (self.get_player(c) is self.turn_player) & \
                                (not ((c.type == ECardType.STRATEGY) & (c.location & ELocation.ON_FIELD > 0) &
                                 c.cover == 1)):
                            for ef in c.effects:
                                if (not ef.trigger) and ef.condition(TimePoint(ETimePoint.ASK4EFFECT)):
                                    efs.append(ef)
                    _len = len(efs)
                    if _len:
                        self.turn_player.output('req_rct', [ETimePoint.ASK4EFFECT])
                        # if self.turn_player.input(lambda yn: 0, 'req_yn'):
                        ef_ind = self.turn_player.free_input(
                            check_ind,
                            'req_chs_eff', [[[ef.host.vid, ef.description] for ef in efs]])
                        # 发动了效果。
                        if ef_ind is not None:
                            self.activate_effect(efs[ef_ind], self.turn_player, TimePoint(ETimePoint.ASK4EFFECT))
                # set 将手牌盖放到场上
                elif cmd[0] == 2:
                    c = self.turn_player.hand[cmd[1]]
                    if c.type == ECardType.EMPLOYEE:
                        self.turn_player.summon_times -= 1
                        self.set_em(self.turn_player, self.turn_player, c, cmd[2])
                    elif c.type == ECardType.STRATEGY:
                        if self.turn_player.set_times:
                            self.turn_player.set_times -= 1
                        else:
                            self.turn_player.strategy_times -= 1
                        self.set_strategy(self.turn_player, self.turn_player, c, None, cmd[2])
                # attack 尝试发动攻击
                elif cmd[0] == 3:
                    attacker = self.turn_player.on_field[cmd[1]]
                    # 模拟攻击以筛选可攻击目标
                    atk_tgt = list()
                    for em in self.op_player.on_field:
                        if em is not None and em.type == ECardType.EMPLOYEE:
                            tp = TimePoint(ETimePoint.TRY_ATTACK, None, [attacker, em, 1])
                            self.enter_time_point(tp)
                            if tp.args[-1]:
                                atk_tgt.append(em.vid)
                    tp = TimePoint(ETimePoint.TRY_ATTACK, None, [attacker, self.op_player.leader, 1])
                    self.enter_time_point(tp)
                    # 入场回合默认不能直接攻击对方领袖。
                    # 风行检查
                    self.enter_time_point(TimePoint(ETimePoint.CHARGE_CHECK, None, attacker))
                    if tp.args[-1] & ((attacker.charge | attacker.turns) > 0):
                        atk_tgt.append(self.op_player.leader.vid)
                        attacker.charge = False
                    _len = len(atk_tgt)
                    tgt_ind = self.turn_player.free_input(check_ind, 'req_atk', [atk_tgt])
                    if tgt_ind is None:
                        continue
                    tgt = self.vid_manager.get_card(atk_tgt[tgt_ind])
                    attacker.attack_times -= 1
                    tp = TimePoint(ETimePoint.ATTACKING, None, [attacker, tgt, 1])
                    self.batch_sending('atk', [attacker.vid, tgt.vid])
                    self.enter_time_point(tp)
                    # 攻击时离场导致攻击无效。
                    if tp.args[-1] & ((attacker.location & ELocation.ON_FIELD) > 0):
                        tgt = tp.args[1]
                        # 对领袖的攻击，询问阻挡
                        if tgt is self.op_player.leader:
                            tgt = self.req4block(attacker, tgt)
                            attacker.attack(tgt, True)
                        else:
                            attacker.attack(tgt)
                # next phase 主动进行自己回合的下个阶段(主要阶段1->战斗阶段1(->战斗阶段2)->主要阶段2->回合结束)
                elif cmd[0] == 4:
                    self.enter_turn_phase(next(ntp))
                # good game 单局认输
                elif cmd[0] == 5:
                    self.win_reason = 2
                    self.winner = self.op_player
                    break
                # change posture 转变姿态
                elif cmd[0] == 6:
                    c = self.turn_player.on_field[cmd[1]]
                    if c.type == ECardType.EMPLOYEE:
                        if c.cover == 1:
                            tp = TimePoint(ETimePoint.UNCOVERING_EM, None, [c, 1])
                            self.batch_sending('crd_cp', [c.vid])
                            self.enter_time_point(tp)
                            if tp.args[-1]:
                                c.cover = 0
                                self.batch_sending('upd_vc', [c.vid, c.serialize()])
                            self.enter_time_point(TimePoint(ETimePoint.UNCOVERED_EM, None, [c]))
                        else:
                            # 先消耗次数
                            c.posture_times -= 1
                            self.change_posture(self.turn_player, c, not c.posture)
                    elif c.type == ECardType.STRATEGY:
                        tp = TimePoint(ETimePoint.UNCOVERING_STRATEGY, None, [c, 1])
                        self.enter_time_point(tp)
                        if tp.args[-1]:
                            self.activate_strategy(self.turn_player, self.turn_player, c, cmd[1])
                        self.enter_time_point(TimePoint(ETimePoint.UNCOVERED_STRATEGY, None, [c]))
                # quick attack 快速攻击指令
                elif cmd[0] == 7:
                    attacker = self.turn_player.on_field[cmd[1]]
                    tgt = self.vid_manager.get_card(cmd[2])
                    attacker.attack_times -= 1
                    tp = TimePoint(ETimePoint.ATTACKING, None, [attacker, tgt, 1])
                    self.enter_time_point(tp)
                    # 攻击时离场导致攻击无效。
                    if tp.args[-1] & ((attacker.location & ELocation.ON_FIELD) > 0):
                        tgt = tp.args[1]
                        self.batch_sending('atk', [attacker.vid, tgt.vid])
                        # 对领袖的攻击，询问阻挡
                        if tgt is self.op_player.leader:
                            tgt = self.req4block(attacker, tgt)
                            attacker.attack(tgt, True)
                        else:
                            attacker.attack(tgt)
                # end turn 主动结束自己回合(主要阶段1->战斗阶段1(->战斗阶段2)->主要阶段2->回合结束)
                elif cmd[0] == 8:
                    while self.turn_phase != ETurnPhase.ENDING:
                        self.enter_turn_phase(next(ntp))

    def next_turn_phase(self):
        for p in self.turn_process:
            yield p

    def enter_turn_phase(self, ph):
        self.batch_sending('ent_tph', [ph], self.turn_player)
        self.turn_phase = ph
        if ph == ETurnPhase.BEGINNING:
            # 重置次数
            self.__beginning()
            self.enter_time_point(TimePoint(ETimePoint.TURN_BEGIN))
        elif ph == ETurnPhase.DP:
            self.enter_time_point(TimePoint(ETimePoint.DP_BEGIN))
            self.__tph_draw_card()
        elif ph == ETurnPhase.M1:
            self.enter_time_point(TimePoint(ETimePoint.M1_BEGIN))
        elif ph == ETurnPhase.BP1:
            self.enter_time_point(TimePoint(ETimePoint.BP1_BEGIN))
        elif ph == ETurnPhase.LBP1:
            self.enter_time_point(TimePoint(ETimePoint.LBP1_BEGIN))
        elif ph == ETurnPhase.LBP2:
            self.enter_time_point(TimePoint(ETimePoint.LBP2_BEGIN))
        elif ph == ETurnPhase.M2:
            self.enter_time_point(TimePoint(ETimePoint.M2_BEGIN))
        elif ph == ETurnPhase.ENDING:
            self.enter_time_point(TimePoint(ETimePoint.TURN_ENDING))
            self.enter_time_point(TimePoint(ETimePoint.TURN_END))
            # 场上全部卡历经回合数+1
            self.__ending()

    def __beginning(self):
        self.turns += 1
        self.skip_times += 1
        if self.skip_times >= self.max_skip:
            self.winner = self.players[self.turn_player.sp]
        # 重置可召唤、适用策略次数。
        self.turn_player.summon_times = 1
        self.turn_player.strategy_times = 1
        self.turn_player.activate_times = 0
        self.turn_player.set_times = 0
        for p in self.players:
            p.ef_limiter = dict()
        for c in self.turn_player.on_field:
            if c is not None and c.type == ECardType.EMPLOYEE:
                c.reset_times()

    def __ending(self):
        for p in self.players:
            for c in p.on_field:
                if c is not None:
                    c.turns += 1

    def __tph_draw_card(self):
        if len(self.turn_player.deck) > 0:
            count = 2 if len(self.turn_player.deck) > 1 else 1
            tp = TimePoint(ETimePoint.TRY_DRAW, None, [count, 1])
            self.enter_time_point(tp)
            if tp.args[-1]:
                self.draw_card(self.turn_player, tp.args[0])

    def give_up(self, p: GamePlayer, is_me):
        """
        一方认输。
        :param p: 当前进行输入的玩家。
        :param is_me:
        :return:
        """
        if self.phase_now == EGamePhase.PLAY_CARD:
            if is_me:
                self.winner = self.players[p.sp]
                self.win_reason = 2
            else:
                self.winner = p
                self.win_reason = 2
            return True
        return False

    def judge(self):
        """
        强制进行单局的胜负判断。
        :return:
        """
        self.winner = self.p1 if self.p1.leader.DEF.value > self.p2.leader.DEF.value else self.p2

    def exchange_turn(self):
        p = self.op_player
        self.op_player = self.turn_player
        self.turn_player = p

    def next_turn(self, ntp):
        self.exchange_turn()
        self.enter_turn_phase(ETurnPhase.BEGINNING)
        self.enter_turn_phase(ETurnPhase.DP)
        self.enter_turn_phase(next(ntp))

    def enter_time_point(self, tp: TimePoint, out: bool = False):
        self.tp_stack.append(tp)
        # if out:
        #     self.batch_sending('ent_tp', [tp.tp])
        if tp.sender is None:
            # 先询问对方。
            self.react_times += 2
            self.react(self.op_player, tp, self.react_times - 2)
        else:
            self.react_times += 2
            self.react(self.players[self.get_player(tp.sender.host).sp], tp, self.react_times - 2)
        self.tp_stack.remove(tp)

    def enter_time_points(self):
        tts = list()
        p = self.turn_player
        while len(self.temp_tp_stack):
            t = self.temp_tp_stack[0]
            self.tp_stack.append(t)
            tts.append(t)
            self.temp_tp_stack.pop(0)
        for t in tts:
            p = p if t.sender is None else self.get_player(t.sender.host)
            # self.batch_sending('ent_tp', [t.tp])
            # 先询问对方。
            self.react_times += 2
            self.react(self.players[p.sp], t, self.react_times - 2)
        # 不需要倒序移除。
        for t in tts:
            self.tp_stack.remove(t)

    def react(self, p: GamePlayer, tp: TimePoint, rt):
        """
        询问p是否连锁。先询问对手。
        :param p: 连锁发起者，被最后询问的人。
        :param tp: 询问连锁的时点。
        :param rt: 进入时的连锁计数，计数值少于这个数值时跳出
        :return:
        """
        def check_eff_ind(ind):
            return 0 if ind in range(0, ind_max) else EErrorCode.OVERSTEP
        p_react_list = list()
        for ef in self.ef_listener:
            if ef.condition(tp) & (not ef.removing) & (tp not in ef.reacted):
                if self.get_player(ef.host) is p:
                    if ef.force:
                        self.activate_effect(ef, p, tp)
                    else:
                        p_react_list.append(ef)
        if len(p_react_list) > 0 or not p.auto_skip:
            p.output('req_rct', [tp.tp])
            # if p.input(lambda yn: 0, 'req_yn'):
            ind_max = len(p_react_list)
            p_react_ef_ind = p.free_input(
                check_eff_ind,
                'req_chs_eff', [[[ef.host.vid, ef.description] for ef in p_react_list]])
            if p_react_ef_ind is not None:
                # 响应了效果。
                self.activate_effect(p_react_list[p_react_ef_ind], p, tp)
                # 3 - 1 = 2
                self.react_times = rt + 3
        self.react_times -= 1
        if self.react_times > rt:
            self.react(self.players[p.sp], tp, rt)
        elif self.react_times == 0:
            for ef in self.ef_listener:
                ef.reacted.clear()
                if ef.removing:
                    self.ef_listener.remove(ef)

    def req4block(self, sender: GameCard, target: GameCard):
        """
        请求阻挡。
        :param sender:
        :param target:
        :return:
        """
        def check_ind(ind):
            if ind not in range(0, blk_tgt_len):
                return EErrorCode.OVERSTEP
            return 0

        blocker = list()
        for em in self.get_player(target).on_field:
            if em is not None and em.type == ECardType.EMPLOYEE:
                # 还有剩余的可阻挡次数
                if em.block_times == 0:
                    continue
                tp = TimePoint(ETimePoint.TRY_BLOCK, None, [sender, em, 1])
                self.enter_time_point(tp)
                if tp.args[-1]:
                    blocker.append(em.vid)
        blk_tgt_len = len(blocker)
        if blk_tgt_len:
            i = self.get_player(target).free_input(check_ind, 'req_blk', [blocker])
            if i is None:
                return target
            tp = TimePoint(ETimePoint.BLOCKING, None, [sender, blocker[i], 1])
            self.enter_time_point(tp)
            if tp.args[-1]:
                self.batch_sending('blk', [tp.args[1]])
                c = self.vid_manager.get_card(tp.args[1])
                c.block_times -= 1
                return c
        return target

    def activate_effect(self, ef: Effect, p: GamePlayer, t: TimePoint = None):
        """
        启动效果。(cost+execute)
        :param ef:
        :param p: 效果发动者。
        :param t: 指定时点，用于询问主动效果。
        :return:
        """
        # 输出。
        if ef.secret:
            p.output('cst_eff', [None if ef.no_source else ef.host.vid, ef.description], True)
            if ef.cost(t):
                # if ef.condition(t):
                p.output('act_eff', [None if ef.no_source else ef.host.vid, ef.description], True)
                ef.execute()
                return
        if not ef.passive:
            for pi in self.players:
                if (not ef.secret) | (pi is p):
                    ef.cover = 0
                    pi.update_vc(ef.host)
                    pi.output('cst_eff', [None if ef.no_source else ef.host.vid, ef.description], pi is p)
        if ef.cost(t):
            tp = TimePoint(ETimePoint.PAID_COST, ef, [ef.host, 1])
            self.temp_tp_stack.append(tp)
            self.enter_time_points()
            # 例：挫折大师的condition需检查是否还有手牌，但是回收时并不需要
            if tp.args[-1]:  # and ef.condition(t):
                # 输出
                if not ef.passive:
                    for pi in self.players:
                        if (not ef.secret) | (pi is p):
                            ef.cover = 0
                            pi.update_vc(ef.host)
                            pi.output('act_eff', [None if ef.no_source else ef.host.vid, ef.description],
                                      pi is p)
                ef.execute()
                self.temp_tp_stack.append(TimePoint(ETimePoint.SUCC_EFFECT_ACTIVATE, ef, ef))
            else:
                self.temp_tp_stack.append(TimePoint(ETimePoint.FAIL_EFFECT_ACTIVATE, ef, ef))
            self.enter_time_points()

    def update_ef_list(self):
        """
        手动刷新ef_list。
        :return:
        """
        self.ef_listener = list()
        for c in self.vid_manager.cards.values():
            for ef in c.effects:
                if ef.act_phase == self.phase_now and ef.trigger:
                    self.ef_listener.append(ef)

    def batch_sending(self, op, args: list = None, sender=None):
        """
        群发消息。
        :return:
        """
        for p in self.players:
            p.output(op, args, True if sender is None else p is sender)

    def get_info(self, p: GamePlayer, cmd: str):
        """
        :param p:
        :param cmd:
        :return: list
        """
        ls = cmd.split(' ')
        c = ls[0]
        # if c == 'vid':
        #     vid = int(ls[1])
        #     if vid in p.vision:
        #         return [self.vid_manager.get_card(vid).serialize()]
        return None

    def get_player(self, c: GameCard) -> GamePlayer:
        """
        获得持有指定卡的玩家。
        :param c:
        :return:
        """
        return self.players[(c.location & ELocation.P1) == 0]

    def get_players(self, c: GameCard):
        """
        [c的持有者, 对手]。
        :param c:
        :return:
        """
        return self.players[(c.location & ELocation.P1) == 0], self.players[(c.location & ELocation.P1) > 0]

    def record(self, p: GamePlayer, msg):
        """
        记录操作，用于卡片效果查询其发动条件是否满足。
        :param p:
        :param msg:
        :return:
        """
        self.event_stack.append((p, msg))

    # -------⬇效果函数(execute部分, 卡片属性的修改也属于此类(gain、become...))⬇--------
    def activate_effect_step2(self, ef: Effect, doing_tp, done_tp,
                              *args):
        """
        适用效果。
        :param ef:
        :param doing_tp: 进行该效果时的时点，用于无效该效果。
        :param done_tp
        :param args
        :return:
        """
        if doing_tp is not None:
            doing_tp = TimePoint(doing_tp, ef, [*args, 1])
            self.enter_time_point(doing_tp)
        if doing_tp.args[-1]:
            args = doing_tp.args
            if ef is None:
                yield True
                if done_tp is not None:
                    done_tp = TimePoint(done_tp, None, args)
                    self.enter_time_point(done_tp)
            elif doing_tp.args[-1]:
                yield True
                if done_tp is not None:
                    done_tp = TimePoint(done_tp, ef, args)
                    self.enter_time_point(done_tp)
            yield True
        else:
            yield False

    def investigate(self, p: GamePlayer, vid, pos):
        """
        在放置阶段时调查卡。
        :param p: 发动效果的玩家
        :param vid:
        :param pos:
        :return:
        """
        c = self.vid_manager.get_card(vid)
        c.cover = 0
        self.batch_sending('upd_vc', [vid, c.serialize()])
        self.batch_sending('upd_cbd', [pos], p)

    def show_card(self, p: GamePlayer, vid, ef: Effect = None, with_tp=True):
        """
        向双方展示自己选择的卡(不包括洗牌, 但必须在之后洗牌)。
        :param p: 发动效果的玩家
        :param vid:
        :param ef: 所属效果，为None表示无源效果
        :param with_tp: 能否响应
        :return:
        """
        if with_tp:
            check_point = self.activate_effect_step2(ef, ETimePoint.SHOWING_CARD, ETimePoint.SHOWED_CARD,
                                                     self.vid_manager.get_card(vid))
            # 没有能无效展示卡的效果所以这里不作判断
            next(check_point)
            self.batch_sending('upd_vc', [vid, self.vid_manager.get_card(vid).serialize()])
            self.batch_sending('shw_crd', [vid], p)
            next(check_point)
        else:
            self.batch_sending('upd_vc', [vid, self.vid_manager.get_card(vid).serialize()])
            self.batch_sending('shw_crd', [vid], p)

    def draw_card(self, p: GamePlayer, draw_count, ef: Effect = None, with_tp=True):
        """
        抽卡。
        :param p: 发动效果的玩家
        :param draw_count: 抽卡数量
        :param ef: 所属效果，为None表示无源效果
        :param with_tp: 能否响应
        :return:
        """
        if with_tp:
            check_point = self.activate_effect_step2(ef, ETimePoint.DRAWING, None, draw_count)
            if next(check_point):
                cs = list()
                for i in range(0, draw_count):
                    if len(p.deck) > 0:
                        c = p.deck[-1]
                        cs.append(c)
                        self.send2hand(p, p, c)
                    else:
                        break
                self.enter_time_point(TimePoint(ETimePoint.DRAWN, None, cs))
        else:
            for i in range(0, draw_count):
                if len(p.deck) > 0:
                    self.send2hand(p, p, p.deck[-1])
                else:
                    break

    def summon(self, p: GamePlayer, pt: GamePlayer, em: GameCard, pos, posture, ef: Effect = None):
        """
        雇员入场。
        :param p: 发起召唤的玩家
        :param pt: player target 召唤到
        :param em: 雇员
        :param pos: 入场位置(0-2)
        :param posture: 入场姿态(非零表示防御姿态)
        :param ef:
        :return:
        """
        cm = em.move_to(ef, ELocation.ON_FIELD + 2 - pt.sp)
        if next(cm):
            self.enter_time_points()
            if next(cm):
                tp = TimePoint(ETimePoint.SUMMONING, ef, [em, pt, pos, posture, 1])
                self.enter_time_point(tp)
                if tp.args[-1]:
                    pt, pos, posture = tp.args[1:4]
                    pt.on_field[pos] = em
                    em.inf_pos = pos
                    em.cover = 0
                    em.posture = (posture == 1)
                    next(cm)
                    # 重置攻击、阻挡次数
                    em.reset_times()
                    # todo: 换em的效果不会出。
                    self.temp_tp_stack.append(TimePoint(ETimePoint.SUCC_SUMMON, ef, [em, pos, posture]))
                    self.batch_sending('upd_vc', [em.vid, em.serialize()])
                    self.batch_sending('smn', [em.vid, int(ef is None)], p)
                    self.enter_time_points()
                self.enter_time_point(TimePoint(ETimePoint.SUMMONED, ef, [em, pos, posture]))

    def special_summon(self, p: GamePlayer, pt: GamePlayer, em: GameCard, ef: Effect, posture=None):
        """
        雇员请求特殊入场。
        :param p: 发起召唤的玩家
        :param pt: player target 召唤到
        :param em: 雇员
        :param ef:
        :param posture
        :return:
        """
        def check_pos(_pos):
            if _pos not in range(0, 3):
                return EErrorCode.OVERSTEP
            if pt.on_field[_pos] is not None:
                return EErrorCode.INVALID_PUT
            return 0

        # 询问入场位置、姿态
        pos = p.input(check_pos, 'req_pos', [pt is p])
        if pos is not None:
            posture = p.input(lambda x: 0, 'req_pst', [0, 2]) > 0 if posture is None else posture
            self.summon(p, pt, em, pos, posture, ef)
            return

    def common_summon(self, p: GamePlayer, pt: GamePlayer, em: GameCard):
        """
        特殊条件下，雇员请求常规入场(如契约策略、成功之子等)，不判断是否还有剩余次数(但会减少)。
        :param p: 发起召唤的玩家
        :param pt: player target 召唤到
        :param em: 雇员
        :param force:
        :return:
        """
        def check_pos(_pos):
            if _pos not in range(0, 3):
                return EErrorCode.OVERSTEP
            if pt.on_field[_pos] is not None:
                return EErrorCode.INVALID_PUT
            return 0
        p.summon_times -= 1
        for posture in range(0, 2):
            for pos in range(0, 3):
                if pt.on_field[pos] is None:
                    tp = TimePoint(ETimePoint.TRY_SUMMON, None, [em, pt, pos, posture, 1])
                    self.enter_time_point(tp)
                    # 入场被允许
                    if tp.args[-1]:
                        # 询问入场位置、姿态
                        pos = p.input(check_pos, 'req_pos', [pt is p])
                        if pos is not None:
                            posture = p.input(lambda x: 0, 'req_pst', [0, 2]) > 0
                            self.summon(p, pt, em, pos, posture, None)
                            return
        # 未成功，送去场下
        self.send_to_grave(p, pt, em)

    def activate_strategy(self, p: GamePlayer, pt: GamePlayer, s: GameCard, pos: int = -1):
        """
        发动策略。
        :param p: 发起者。
        :param pt: 在目标玩家的场上发动。
        :param s: 
        :param pos:
        :return: 
        """
        cm = s.move_to(None, ELocation.ON_FIELD + 2 - pt.sp)
        next(cm)
        self.enter_time_points()
        if next(cm):
            if pos == -1:
                def check_pos(_pos):
                    if _pos not in range(3, 6):
                        return EErrorCode.OVERSTEP
                    if pt.on_field[_pos] is not None:
                        return EErrorCode.INVALID_PUT
                    return 0

                # 询问入场位置、姿态
                pos = p.input(check_pos, 'req_pos_stg', [pt is p])
            pt.on_field[pos] = s
            s.posture = 0
            s.inf_pos = pos
            s.cover = 0
            next(cm)
            self.batch_sending('upd_vc', [s.vid, s.serialize()])
            self.batch_sending('act_stg', [s.vid], p)
            tp = TimePoint(ETimePoint.ACTIVATING_STRATEGY, None, [s, 1])
            self.enter_time_point(tp)
            # 发动成功
            if tp.args[-1]:
                # todo: 换s的效果不会出。
                self.temp_tp_stack.append(TimePoint(ETimePoint.SUCC_ACTIVATE_STRATEGY, None, [s]))
                # 策略使用时自动发动效果。
                self.activate_effect(s.effects[0], p)
                self.enter_time_points()
                # 非持续/单人策略发动后离场
                if ((s.subtype & EStrategyType.LASTING) > 0) | ((s.subtype & EStrategyType.ATTACHMENT) > 0):
                    return
        if (s.location & ELocation.ON_FIELD) > 0:
            self.send_to_grave(p, p, s)

    def set_em(self, p: GamePlayer, pt: GamePlayer, em: GameCard, pos, ef: Effect = None):
        """
        盖放秘密雇员。
        :param p:
        :param pt: 在目标玩家的场上盖放。
        :param em:
        :param pos:
        :param ef:
        :return:
        """
        cm = em.move_to(None, ELocation.ON_FIELD + 2 - pt.sp)
        next(cm)
        self.enter_time_points()
        if next(cm):
            tp = TimePoint(ETimePoint.SET_EM, ef, [em, 1])
            self.enter_time_point(tp)
            if tp.args[-1]:
                pt.on_field[pos] = em
                em.inf_pos = pos
                em.cover = 1
                next(cm)
                for pi in self.players:
                    if pi is p:
                        pi.update_vc(em)
                    else:
                        pi.update_vc_ano(em)
                        pi.output('upd_vc_ano', [em.vid, em.serialize_anonymous()])
                self.batch_sending('set_crd', [em.vid], p)
                self.enter_time_points()

    def set_strategy(self, p: GamePlayer, pt: GamePlayer, s: GameCard, ef: Effect = None, pos: int = -1):
        """
        盖放策略。
        :param p:
        :param pt: 在目标玩家的场上盖放。
        :param s:
        :param pos:
        :param ef:
        :return:
        """
        cm = s.move_to(None, ELocation.ON_FIELD + 2 - pt.sp)
        next(cm)
        self.enter_time_points()
        if next(cm):
            tp = TimePoint(ETimePoint.SET_STRATEGY, ef, [s, 1])
            self.enter_time_point(tp)
            if tp.args[-1]:
                if pos == -1:
                    def check_pos(_pos):
                        if _pos not in range(3, 6):
                            return EErrorCode.OVERSTEP
                        if pt.on_field[_pos] is not None:
                            return EErrorCode.INVALID_PUT
                        return 0

                    # 询问入场位置、姿态
                    pos = p.input(check_pos, 'req_pos_stg', [pt is p])
                pt.on_field[pos] = s
                s.inf_pos = pos
                s.cover = 1
                if (s.subtype & EStrategyType.COUNTER) > 0:
                    s.posture = 1
                else:
                    s.posture = 0
                next(cm)
                for pi in self.players:
                    if pi is p:
                        pi.output('upd_vc', [s.vid, s.serialize()])
                    else:
                        pi.output('upd_vc_ano', [s.vid, s.serialize_anonymous()])
                self.batch_sending('set_crd', [s.vid], p)
                self.enter_time_points()

    def send_to(self, loc, p: GamePlayer, pt: GamePlayer, c: GameCard, ef: Effect = None, shuffle=True):
        f = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [c, 1])
            self.enter_time_point(tp)
            f = tp.args[-1]
        if f:
            cm = c.move_to(ef, loc)
            next(cm)
            self.enter_time_points()
            if next(cm):
                next(cm)
                if loc & ELocation.GRAVE:
                    self.batch_sending('upd_vc', [c.vid, c.serialize()])
                else:
                    cov = c.cover
                    for pi in self.players:
                        if (not cov) | (pi is pt):
                            pi.output('upd_vc', [c.vid, c.serialize()])
                        else:
                            pi.output('upd_vc_ano', [c.vid, c.serialize_anonymous()])
                    # todo: 换c的效果不会出。
                    self.batch_sending('crd_snd', [c.vid, loc], p)
                    self.enter_time_points()
                    if ((loc & ELocation.EXILED) == 0) & shuffle:
                        pt.shuffle(loc - 2 + pt.sp)
                return True
        return False

    def send_to_grave(self, p: GamePlayer, pt: GamePlayer, c: GameCard, ef: Effect = None):
        """
        送去墓地。
        :param p:
        :param pt: 送去目标玩家的墓地。
        :param c:
        :param ef:
        :return:
        """
        f = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [c, 1])
            self.enter_time_point(tp)
            f = tp.args[-1]
        if f:
            cm = c.move_to(ef, ELocation.GRAVE + 2 - pt.sp)
            next(cm)
            self.enter_time_points()
            if next(cm):
                next(cm)
                # 墓地的卡必须公开。
                self.batch_sending('upd_vc', [c.vid, c.serialize()])
                # todo: 换c的效果不会出。
                self.batch_sending('crd_snd2grv', [c.vid], p)
                self.enter_time_points()

    def send2hand(self, p: GamePlayer, pt: GamePlayer, c: GameCard, ef: Effect = None, shuffle=True):
        """
        送去手牌。
        :param p:
        :param pt: 送去目标玩家的手牌。
        :param c:
        :param ef:
        :param shuffle:
        :return:
        """
        f = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [c, 1])
            self.enter_time_point(tp)
            f = tp.args[-1]
        if f:
            cov = c.cover
            cm = c.move_to(ef, ELocation.HAND + 2 - pt.sp)
            next(cm)
            self.enter_time_points()
            if next(cm):
                next(cm)
                for pi in self.players:
                    if (cov == 0) | (pi is pt):
                        pi.output('upd_vc', [c.vid, c.serialize()])
                    else:
                        pi.output('upd_vc_ano', [c.vid, c.serialize_anonymous()])
                # todo: 换c的效果不会出。
                self.batch_sending('crd_snd2hnd', [c.vid], p)
                self.enter_time_points()
                if shuffle:
                    pt.shuffle()

    def send2deck(self, p: GamePlayer, pt: GamePlayer, c: GameCard, ef: Effect = None, ind=-1):
        """
        送去卡组。
        :param p:
        :param pt: 送去目标玩家的卡组。
        :param c:
        :param ef:
        :param ind:
        :return:
        """
        f = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [c, 1])
            self.enter_time_point(tp)
            f = tp.args[-1]
        if f:
            cov = c.cover
            cm = c.move_to(ef, ELocation.DECK + 2 - pt.sp, ind)
            next(cm)
            self.enter_time_points()
            if next(cm):
                next(cm)
                for pi in self.players:
                    if (cov == 0) | (pi is pt):
                        pi.output('upd_vc', [c.vid, c.serialize()])
                    else:
                        pi.output('upd_vc_ano', [c.vid, c.serialize_anonymous()])
                # todo: 换c的效果不会出。
                self.batch_sending('crd_snd2dck', [c.vid], p)
                pt.output('dck', [cc.vid for cc in p.deck])
                self.enter_time_points()

    def send2exiled(self, p: GamePlayer, pt: GamePlayer, c: GameCard, ef: Effect = None):
        """
        送去移除区。
        :param p:
        :param pt: 送去目标玩家的移除区。
        :param c:
        :param ef:
        :return:
        """
        f = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [c, 1])
            self.enter_time_point(tp)
            f = tp.args[-1]
        if f:
            cov = c.cover
            cm = c.move_to(ef, ELocation.EXILED + 2 - pt.sp)
            next(cm)
            self.enter_time_points()
            if next(cm):
                next(cm)
                for pi in self.players:
                    if (cov == 0) | (pi is pt):
                        pi.output('upd_vc', [c.vid, c.serialize()])
                    else:
                        pi.output('upd_vc_ano', [c.vid, c.serialize_anonymous()])
                # todo: 换c的效果不会出。
                self.batch_sending('crd_snd2exd', [c.vid], p)
                self.enter_time_points()
                return True
        return False

    def deal_damage(self, sender: GameCard, target: GameCard, damage: int, ef: Effect = None):
        """
        造成伤害。注意：等于0时并不会被无效(因为需要呈现-0的伤害值给玩家作反馈)。
        :param sender: 伤害来源。
        :param target: 目标。
        :param damage: 伤害量。
        :param ef:
        :return:
        """
        f = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [target, 1])
            self.enter_time_point(tp)
            f = tp.args[-1]
        if f:
            tp = TimePoint(ETimePoint.DEALING_DAMAGE, ef, [sender, target, damage, 1])
            self.enter_time_point(tp)
            if tp.args[-1]:
                sender, target, damage = tp.args[:-1]
                # gain会通知客户端。
                target.DEF.gain(-damage, False, ef)
                # todo: 是特性，不是bug。
                self.batch_sending('dmg', [target.vid, damage], self.get_player(sender))
                self.enter_time_point(TimePoint(ETimePoint.DEALT_DAMAGE, ef, [sender, target, damage]))

    def heal(self, sender: GameCard, target: GameCard, value: int, ef: Effect):
        """
        回复。注意：等于0时并不会被无效(因为需要呈现+0的值给玩家作反馈)。
        :param sender: 来源。
        :param target: 目标。
        :param value: 回复量。
        :param ef:
        :return:
        """
        f = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [target, 1])
            self.enter_time_point(tp)
            f = tp.args[-1]
        if f:
            tp = TimePoint(ETimePoint.HEALING, ef, [sender, target, value, 1])
            self.enter_time_point(tp)
            if tp.args[-1]:
                sender, target, value = tp.args[:-1]
                # gain会通知客户端。
                target.DEF.gain(value, False, ef)
                # todo: 是特性，不是bug。
                self.batch_sending('hea', [target.vid, value], self.get_player(sender))
                self.enter_time_point(TimePoint(ETimePoint.HEALED, ef, [sender, target, value]))

    def destroy(self, sender: GameCard, target: GameCard, ef: Effect = None):
        """
        摧毁指定的卡。
        :param sender: 摧毁者。
        :param target: 被摧毁的目标卡。
        :param ef:
        :return:
        """
        f = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [target, 1])
            self.enter_time_point(tp)
            f = tp.args[-1]
        if f:
            tp = TimePoint(ETimePoint.DESTROYING, ef, [sender, target, 1])
            self.enter_time_point(tp)
            if tp.args[-1]:
                sender, target = tp.args[:-1]
                tp = TimePoint(ETimePoint.DESTROYING_SURE, ef, [sender, target])
                self.enter_time_point(tp)
                if target.type == ECardType.LEADER:
                    self.winner = self.players[self.get_player(target).sp]
                    self.win_reason = 0
                else:
                    # todo: 是特性，不是bug。
                    self.batch_sending('crd_des', [target.vid], self.get_player(sender))
                    self.send_to_grave(self.get_player(sender), self.get_player(target), target, ef)
                    self.enter_time_point(TimePoint(ETimePoint.DESTROYED, ef, [sender, target]))

    def choose_target_from_func(self, p: GamePlayer, pt: GamePlayer, func,
                                ef: Effect, force=True, with_tp=True, count=1):
        """
        选择效果目标。效果的host(宿主)一定是效果的发动者。已经包含了TRY_CHOOSE_TARGET。
        :param p:
        :param pt:
        :param func:  筛选函数。
        :param ef:
        :param force: 是否强制
        :param with_tp:
        :param count:
        :return:
        """
        cs = list()
        if with_tp:
            for c in self.vid_manager.get_cards():
                if func(c):
                    # 模拟选择。
                    tp = TimePoint(ETimePoint.TRY_CHOOSE_TARGET, ef, [c, count])
                    self.enter_time_point(tp)
                    if tp.args[-1]:
                        cs.append(c.vid)
            return self.choose_target(p, pt, cs, ef, force, True, count)
        else:
            for c in self.vid_manager.get_cards():
                if func(c):
                    cs.append(c.vid)
            return self.choose_target(p, pt, cs, ef, force, False, count)
        return None

    def choose_target(self, p: GamePlayer, pt: GamePlayer, cs,
                      ef: Effect, force=True, with_tp=True, count=1):
        """
        选择效果目标。效果的host(宿主)一定是效果的发动者。已经包含了TRY_CHOOSE_TARGET。
        :param p:
        :param pt:
        :param cs: 选项。
        :param ef:
        :param force: 是否强制
        :param with_tp:
        :param count: 为负时其绝对值表示不选的个数。比如0表示必须全选，-1表示必须剩且仅剩1个不选。
        :return:
        """
        return self.choose_target_complex(p, pt, cs, ef, force, with_tp, count, count)

    def choose_target_complex(self, p: GamePlayer, pt: GamePlayer, cs,
                      ef: Effect, force=True, with_tp=True, at_most=1, at_least=1):
        def check_ind(*_args):
            if (len(_args) < at_least) | (len(_args) > at_most):
                return EErrorCode.ILLEGAL_OPTIONS
            _ins = dict()
            for _ind in _args:
                if _ind not in range(0, _len):
                    return EErrorCode.OVERSTEP
                if _ind in _ins.keys():
                    return EErrorCode.REPEAT_CHOOSE
                _ins[_ind] = 1
            return 0

        _len = len(cs)
        if at_most <= 0:
            at_most = _len - at_most
        if at_least <= 0:
            at_least = _len - at_least
        if at_least > at_most:
            return None
        if (_len >= at_least) & (_len > 0):
            # 打乱
            for i in range(0, _len):
                j = randint(0, _len - 1)
                temp = cs[j]
                cs[j] = cs[i]
                cs[i] = temp
            # 询问选项
            if force:
                ind = pt.input(check_ind, 'req_chs_tgt', [cs, at_least, at_most])
            else:
                ind = pt.free_input(check_ind, 'req_chs_tgt', [cs, at_least, at_most])
                if ind is None:
                    return None
        else:
            return None
        if type(ind) is list:
            tgts = list()
            for i in ind:
                c = self.vid_manager.get_card(cs[i])
                if with_tp:
                    tp = TimePoint(ETimePoint.CHOOSING_TARGET, ef, [c, 1])
                    self.enter_time_point(tp)
                    if tp.args[-1]:
                        self.enter_time_point(TimePoint(ETimePoint.CHOSE_TARGET, ef, [c]))
                        tgts.append(c)
                else:
                    tgts.append(c)
            return tgts
        else:
            c = self.vid_manager.get_card(cs[ind])
            if with_tp:
                tp = TimePoint(ETimePoint.CHOOSING_TARGET, ef, [c, 1])
                self.enter_time_point(tp)
                if tp.args[-1]:
                    self.enter_time_point(TimePoint(ETimePoint.CHOSE_TARGET, ef, [c]))
                    return c
            else:
                return c
        return None

    def ceremony(self, p: GamePlayer, func, v, send_to=ELocation.GRAVE, op='>', with_tp=True):
        """
        进行契约。
        :param p:
        :param func: 素材的筛选函数
        :param send_to: 素材使用后送去……
        :param v: 契约需求的值
        :param op: 操作符。>: 大于等于 =: 恰好等于
        :param with_tp:
        :return:
        """
        def check_ind(_ind):
            if _ind not in range(0, len(cs)):
                return EErrorCode.OVERSTEP
            return 0

        cs = list()
        material = list()
        atk = 0
        if not with_tp:
            for c in self.vid_manager.get_cards():
                if func(c):
                    cs.append(c.vid)
            while True:
                # 询问选项
                ind = p.free_input(check_ind, 'req_chs_tgt', [cs, 1, 1])
                if ind is None:
                    return False
                c = self.vid_manager.get_card(cs[ind])
                material.append(c)
                cs.pop(ind)
                atk += c.ATK.value
                if op == '>':
                    if atk >= v:
                        break
                elif op == '=':
                    if atk == v:
                        break
            for c in material:
                pt = self.get_player(c)
                if not self.send_to(2 - pt.sp + send_to, p, pt, c):
                    return False
            return True
        return False

    def devote(self, p: GamePlayer, c: GameCard, ef: Effect):
        """
        奉献。
        :param p:
        :param c:
        :param ef:
        :return:
        """
        f = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [c, 1])
            self.enter_time_point(tp)
            f = tp.args[-1]
        if f:
            tp = TimePoint(ETimePoint.DEVOTING, ef, [c, 1])
            self.enter_time_point(tp)
            if tp.args[-1]:
                self.send_to_grave(p, p, c, ef)
                self.enter_time_point(TimePoint(ETimePoint.DEVOTED, ef, [c]))
                return True
            return False

    def discard(self, p: GamePlayer, pt: GamePlayer, c: GameCard, ef: Effect):
        """
        丢弃指定的手牌。
        :param p: 效果发起者。
        :param pt: 目标玩家
        :param c: 要丢弃的卡。
        :param ef:
        :return:
        """
        tp = TimePoint(ETimePoint.DISCARDING, ef, [c, 1])
        self.enter_time_point(tp)
        if tp.args[-1]:
            if c.location & ELocation.HAND:
                self.send_to_grave(p, pt, c, ef)
                self.enter_time_point(TimePoint(ETimePoint.DISCARDED, ef, [c]))
                return True
        return False

    def req4discard(self, p: GamePlayer, pt: GamePlayer, count, ef: Effect):
        """
        选择指定的手牌丢弃。
        :param p: 。
        :param pt:
        :param count: 丢弃数量
        :param ef:
        :return:
        """
        def check_discard(c):
            if c in p.hand:
                tp = TimePoint(ETimePoint.TRY_DISCARD, ef, [c, True, 1])
                self.enter_time_point(tp)
                if tp.args[-1]:
                    return True

        # 选择1张卡丢弃
        tgt = self.choose_target_from_func(p, p, check_discard, ef, False, False)
        if tgt is not None:
            self.discard(p, pt, tgt, ef)
            return tgt
        return None

    def req4grave(self, func, p: GamePlayer, pt: GamePlayer, count, ef: Effect):
        """
        选择指定的牌送去场下。
        :param p: 。
        :param pt:
        :param func: 检查函数
        :param count: 移除数量
        :param ef:
        :return:
        """
        def check(c):
            tp = TimePoint(ETimePoint.IN_GRAVE, ef, [c, 1])
            self.enter_time_point(tp)
            if tp.args[-1]:
                return func(c)

        # 选择1张卡移除
        tgt = self.choose_target_from_func(p, p, check, ef, False, False)
        if tgt is not None:
            self.send_to_grave(p, pt, tgt, ef)
            return tgt
        return None

    def req4exile(self, func, p: GamePlayer, pt: GamePlayer, count, ef: Effect):
        """
        选择指定的牌移除。
        :param p: 。
        :param pt:
        :param func: 检查函数
        :param count: 移除数量
        :param ef:
        :return:
        """
        def check(c):
            tp = TimePoint(ETimePoint.IN_EXILED, ef, [c, 1])
            self.enter_time_point(tp)
            if tp.args[-1]:
                return func(c)

        # 选择1张卡移除
        tgt = self.choose_target_from_func(p, p, check, ef, False, False)
        if tgt is not None:
            self.send2exiled(p, pt, tgt, ef)
            return tgt
        return None

    def invalid_effect(self, tgt: GameCard, tgt_ef: Effect, ef: Effect):
        if (not tgt_ef.no_reset) and tgt_ef.can_invalid:
            _tp = TimePoint(ETimePoint.INFLUENCING, ef, [tgt, 1])
            self.enter_time_point(_tp)
            if _tp.args[-1]:
                tgt.remove_effect(tgt_ef)

    def invalid_tp(self, tp: TimePoint, tgt: GameCard, ef: Effect):
        _tp = TimePoint(ETimePoint.INFLUENCING, ef, [tgt, 1])
        self.enter_time_point(_tp)
        if _tp.args[-1]:
            tp.args[-1] = 0

    def change_posture(self, p: GamePlayer, c: GameCard, pst, ef: Effect = None):
        """
        改变至指定的姿态。
        :param p: 效果发起者。
        :param c: 要改变姿态的卡。
        :param pst: 改变至……姿态。
        :param ef:
        :return:
        """
        f = True
        if ef is not None:
            tp = TimePoint(ETimePoint.INFLUENCING, ef, [c, 1])
            self.enter_time_point(tp)
            f = tp.args[-1]
        if f:
            tp = TimePoint(ETimePoint.CHANGING_POSTURE, None, [c, 1])
            self.batch_sending('crd_cp', [c.vid])
            self.enter_time_point(tp)
            if tp.args[-1]:
                c.posture = pst
                self.batch_sending('upd_vc', [c.vid, c.serialize()])
            self.enter_time_point(TimePoint(ETimePoint.CHANGED_POSTURE, None, [c]))

    def count(self, c: GameCard, name, count=1):
        """
        为卡片增加指定种类的计数。
        :param c:
        :param name:
        :param count:
        :return:
        """
        if name in c.sign:
            c.sign[name] += count
        else:
            c.sign[name] = count
        for p in self.players:
            if (p is self.get_player(c)) | (c.cover == 0):
                p.update_vc(c)

    def control(self, p: GamePlayer, pt: GamePlayer, em: GameCard, ef: Effect = None):
        """
        控制对方雇员。
        :param p: 发起的玩家
        :param pt: player target 召唤到
        :param em: 雇员
        :param pos: 入场位置(0-2)
        :param ef:
        :return:
        """
        def check_pos(_pos):
            if _pos not in range(0, 3):
                return EErrorCode.OVERSTEP
            if pt.on_field[_pos] is not None:
                return EErrorCode.INVALID_PUT
            return 0
        # 询问入场位置
        pos = p.input(check_pos, 'req_pos', [pt is p])
        if pos is not None:
            cm = em.move_to(ef, ELocation.ON_FIELD + 2 - pt.sp)
            if next(cm):
                self.enter_time_points()
                if next(cm):
                    tp = TimePoint(ETimePoint.TRY_CONTROL, ef, [em, 1])
                    self.enter_time_point(tp)
                    if tp.args[-1]:
                        next(cm)
                        em = tp.args[0]
                        pt.on_field[pos] = em
                        em.inf_pos = pos
                        # 重置攻击、阻挡次数
                        em.reset_times()
                        self.batch_sending('upd_vc', [em.vid, em.serialize()])
                        self.batch_sending('ctn', [em.vid], p)
