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
        # 可从手牌发动策略的剩余次数。通常情况下每回合1次。
        self.strategy_times = 1
        # 是否为先手玩家。
        self.sp = 0
        # 是否可继续连锁。
        self.can_react = 1
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
        self.leader = GameCard(g, self.leader_id, 2 - self.sp)
        hd = list()
        sd = list()
        for cid in self.ori_deck.keys():
            for i in range(self.ori_deck[cid][0]):
                if int(self.ori_deck[cid][3]):
                    gc = GameCard(g, cid, ELocation.SIDE + 2 - self.sp)
                    # self.vision.append(gc.vid)
                    sd.append(gc)
                else:
                    gc = GameCard(g, cid, ELocation.HAND + 2 - self.sp)
                    # self.vision.append(gc.vid)
                    hd.append(gc)
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
        return self.in_method(self, make_input(*args), func)

    def free_input(self, func, *args):
        return self.in_method(self, make_input(*args), func, False)

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
        for p in self.game.players:
            self.output('upd_vc', [p.leader.vid, p.leader.serialize()], self is p)
            if p != self:
                for c in p.hand:
                    self.update_vc_ano(c)

    def shuffle(self, loc=ELocation.HAND):
        cs = list()
        if loc == ELocation.HAND:
            cs = self.hand
        elif loc == ELocation.DECK:
            cs = self.deck
        elif loc == ELocation.SIDE:
            cs = self.side
        for c in cs:
            self.game.vid_manager.change(c.vid)
        # g: Game = self.game
        for p in self.game.players:
            p.output('shf', [loc + 2 - self.sp])
            if p is self:
                for c in self.hand:
                    self.update_vc(c)
            else:
                for c in self.hand:
                    p.update_vc_ano(c)

    def update_vc(self, c):
        self.output('upd_vc', [c.vid, c.serialize()])

    def update_vc_ano(self, c):
        self.output('upd_vc_ano', [c.vid, c.serialize_anonymous()])


class ObjList(list):
    def remove(self, obj) -> None:
        for i in range(0, len(self)):
            if obj is self[i]:
                self.pop(i)
                return


class CardProperty:
    def __init__(self, v, tp1, tp2, c):
        """

        :param v: 初始值。
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
        self.op_st = ObjList()
        # 数值栈。
        self.val_st = ObjList()
        self.tp1 = tp1
        self.tp2 = tp2
        self.card = c

    def reset(self):
        for i in range(0, len(self.op_st)):
            if self.op_st[i] in '+*=+x*x=x':
                self.op_st.pop(i)
                self.val_st.pop(i)
                i -= 1
        self.update()

    def update(self):
        temp = self.value
        v = self.src_value + self.add_val
        i = 0
        for op in self.op_st:
            if (op == '+') | (op == '++'):
                v += self.val_st[i]
            elif (op == '*') | (op == '**'):
                v *= self.val_st[i]
            elif (op == '=') | (op == '=='):
                v = self.val_st[i]
            elif (op == '+x') | (op == '++x'):
                # 回调函数。
                x = self.val_st[i]
                v += x(self.card)
            elif (op == '*x') | (op == '**x'):
                x = self.val_st[i]
                v *= x(self.card)
            elif (op == '=x') | (op == '==x'):
                x = self.val_st[i]
                v = x(self.card)
            i += 1
        self.value = v if v > 0 else 0
        t1 = TimePoint(self.tp1, None, self.value)
        g = self.card.game
        g.enter_time_point(t1)
        self.value = int(t1.args) if t1.args > 0 else 0
        g.enter_time_point(TimePoint(self.tp2, None, self.value))
        # 发送属性更新信息。
        if temp != self.value:
            for p in self.card.game.players:
                if (p is g.get_player(self.card)) | (not self.card.cover):
                    p.update_vc(self.card)

    def gain(self, v, perm: bool = False):
        """
        攻击力上升/下降。
        :param v:
        :param perm: 是否永久。
        :return:
        """
        new_op = '++' if perm else '+'
        self.op_st.append(new_op)
        self.val_st.append(v)
        self.update()
        return new_op, v

    def gain_x(self, x, perm: bool = False):
        new_op = '++x' if perm else '+x'
        self.op_st.append('++x' if perm else '+x')
        self.val_st.append(x)
        self.update()
        return new_op, x

    def become(self, v, perm: bool = False):
        new_op = '==' if perm else '='
        self.op_st.append('==' if perm else '=')
        self.val_st.append(v)
        self.update()
        return new_op, v

    def become_x(self, x, perm: bool = False):
        new_op = '==x' if perm else '=x'
        self.op_st.append('==x' if perm else '=x')
        self.val_st.append(x)
        self.update()
        return new_op, x

    def ratio(self, v, perm: bool = False):
        new_op = '**' if perm else '*'
        self.op_st.append('**' if perm else '*')
        self.val_st.append(v)
        self.update()
        return new_op, v

    def ration_x(self, x, perm: bool = False):
        new_op = '**x' if perm else '*x'
        self.op_st.append('**x' if perm else '*x')
        self.val_st.append(x)
        self.update()
        return new_op, x

    def remove(self, op, v):
        self.op_st.remove(op)
        self.val_st.remove(v)
        self.update()

    def change_adv(self, adv):
        self.add_val = adv
        self.update()


class HPProperty(CardProperty):
    def update(self):
        super().update()
        if self.value <= 0:
            self.card.game.destroy(None, self.card)


class GameCard:
    def __init__(self, g, cid, ori_loc, is_token=False):
        """

        :param cid:
        :param ori_loc: 初始位置。
        :param is_token:
        """
        # visual id 模拟实际的玩家视野，洗牌等行为后vid改变
        self.vid = 0
        self.game = g
        g.vid_manager.register(self)
        self.cid = cid
        self.name = rds.hget(cid, 'name').decode()
        self.type = int(rds.hget(cid, 'type').decode())
        self.subtype = int(rds.hget(cid, 'subtype').decode())
        self.rank = int(rds.hget(cid, 'rank').decode())
        # 不可修改。
        self.src_atk = int(rds.hget(cid, 'atk_eff').decode())
        self.src_def = int(rds.hget(cid, 'def_hp').decode())
        self.ATK = CardProperty(self.src_atk, ETimePoint.ATK_CALCING, ETimePoint.ATK_CALC, self)
        if self.type == ECardType.LEADER:
            self.DEF = HPProperty(self.src_def, ETimePoint.DEF_CALCING, ETimePoint.DEF_CALC, self)
            self.cover = 0
        else:
            self.DEF = CardProperty(self.src_def, ETimePoint.DEF_CALCING, ETimePoint.DEF_CALC, self)
            # 是否被暗置(背面朝上，对对方玩家不可见)。
            self.cover = 1
        self.series = json.loads(rds.hget(cid, 'series').decode())
        self.is_token = is_token
        self.effects = list()
        self.location = ori_loc
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
        m = import_module('cards.c{}'.format(self.cid))
        m.give(self)

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
                    if (p is self.game.get_player(self)) | (not self.cover):
                        p.update_vc(self)
                    else:
                        p.update_vc_ano(self)
        if e.act_phase == self.game.phase_now and e.trigger:
            self.game.ef_listener.append(e)

    def remove_effect(self, e, out=True):
        self.effects.remove(e)
        if e in self.buff_eff:
            self.buff_eff.pop(e)
            # 通知双方
            if out:
                for p in self.game.players:
                    if (p is self.game.get_player(self)) | (not self.cover):
                        p.update_vc(self)
                    else:
                        p.update_vc_ano(self)
        if e in self.game.ef_listener:
            self.game.ef_listener.remove(e)

    def reset(self):
        """
        离场时，清除所有非永久的buff，效果复原。
        :return:
        """
        for e in self.effects:
            if not e.no_reset:
                self.remove_effect(e)  # , False)
        m = import_module('cards.c{}'.format(self.cid))
        m.give(self)
        # self.attack_times = 0
        # self.block_times = 0
        self.ATK.reset()
        self.DEF.reset()
        self.turns = 0

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
        if tp.args[-1] & (p > v):
            yield True
            tp = TimePoint(ETimePoint.HP_COSTING, ef, [self, v, 1])
            self.game.enter_time_point(tp)
            if tp.args[-1]:
                # 代支付
                c, v = tp.args[:-1]
                if c.type == ECardType.STRATEGY:
                    c.ATK.gain(-v)
                else:
                    c.DEF.gain(-v)
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
            if target.posture:
                if self.ATK.value > target.DEF.value:
                    self.game.destroy(self, target)
                elif self.ATK.value < target.DEF.value:
                    self.game.destroy(target, self)
            elif block:
                if self.ATK.value > target.DEF.value:
                    self.game.destroy(self, target)
                elif self.ATK.value < target.DEF.value:
                    self.game.destroy(target, self)
                self.game.temp_tp_stack.append(TimePoint(ETimePoint.BLOCKED, None, [self, target]))
            else:
                if self.ATK.value > target.ATK.value:
                    self.game.destroy(self, target)
                elif self.ATK.value < target.ATK.value:
                    self.game.destroy(target, self)
                elif self.ATK.value == target.ATK.value:
                    self.game.destroy(self, target)
                    self.game.destroy(target, self)
        self.game.temp_tp_stack.append(TimePoint(ETimePoint.ATTACKED, None, [self, target]))
        self.game.enter_time_points()

    def reset_times(self):
        self.attack_times = 1
        self.block_times = 1
        if self.game.turn_phase == ETurnPhase.BEGINNING:
            self.posture_times = 1
        self.game.enter_time_point(TimePoint(ETimePoint.RESET_TIMES, None, self))

    def move_to(self, ef, loc):
        """
        移动至另一个区域。不能单独使用(但移动区域时必须调用)，不会触发时点。
        :param ef: effect
        :param loc:
        :return:
        """
        if loc != self.location:
            p = self.game.players[(self.location & ELocation.P1) == 0]

            def leave():
                if self.location & ELocation.HAND:
                    return ETimePoint.OUT_HAND, ETimePoint.OUT_HAND_END, p.hand
                if self.location & ELocation.DECK:
                    return ETimePoint.OUT_DECK, ETimePoint.OUT_DECK_END, p.deck
                if self.location & ELocation.SIDE:
                    return ETimePoint.OUT_SIDE, ETimePoint.OUT_SIDE_END, p.side
                if self.location & ELocation.ON_FIELD:
                    # 离场时重置
                    self.reset()
                    return ETimePoint.OUT_FIELD, ETimePoint.OUT_FIELD_END, p.on_field
                if self.location & ELocation.GRAVE:
                    return ETimePoint.OUT_GRAVE, ETimePoint.OUT_GRAVE_END, p.grave
                if self.location & ELocation.EXILED:
                    return ETimePoint.OUT_EXILED, ETimePoint.OUT_EXILED_END, p.exiled

            def enter():
                if loc & ELocation.HAND:
                    self.turns = 0
                    self.cover = 1
                    return ETimePoint.IN_HAND, ETimePoint.IN_HAND_END, p.hand
                if loc & ELocation.DECK:
                    self.turns = 0
                    self.cover = 1
                    return ETimePoint.IN_DECK, ETimePoint.IN_DECK_END, p.deck
                if loc & ELocation.SIDE:
                    self.turns = 0
                    self.cover = 1
                    return ETimePoint.IN_SIDE, ETimePoint.IN_SIDE_END, p.side
                if loc & ELocation.ON_FIELD:
                    self.turns = 0
                    return ETimePoint.IN_FIELD, ETimePoint.IN_FIELD_END, p.on_field
                if loc & ELocation.GRAVE:
                    self.turns = 0
                    self.cover = 0
                    return ETimePoint.IN_GRAVE, ETimePoint.IN_GRAVE_END, p.grave
                if loc & ELocation.EXILED:
                    self.turns = 0
                    return ETimePoint.IN_EXILED, ETimePoint.IN_EXILED_END, p.exiled

            # 离开我放半场去到对方半场不算离场，其他区域同理
            etp1, etp3, _from = leave()
            etp2, etp4, _to = enter()
            tp1 = TimePoint(etp1, ef, [self, 1])
            tp2 = TimePoint(etp2, ef, [self, 1])
            self.game.temp_tp_stack.append(tp1)
            self.game.temp_tp_stack.append(tp2)
            yield True
            yield tp1.args[-1] & tp2.args[-1]
            # 离开, 离场需特殊处理，不能直接remove
            if self.location & ELocation.ON_FIELD:
                p.on_field[self.inf_pos] = None
            else:
                _from.remove(self)
            # 进入, 入场的具体位置不在这里处理
            self.location = loc
            if (loc & ELocation.ON_FIELD) == 0:
                _to.append(self)
            tp3 = TimePoint(etp3, ef, self)
            tp4 = TimePoint(etp4, ef, self)
            self.game.temp_tp_stack.append(tp3)
            self.game.temp_tp_stack.append(tp4)
            yield True
        else:
            yield False
            yield True
            yield True

    def serialize(self):
        return {
            'vid': self.vid,
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
            'posture': self.posture,
            'cover': self.cover,
                           }

    def serialize_anonymous(self):
        return {
            'vid': self.vid,
            'add_val': self.ATK.add_val,
            'location': self.location,
            'buff_eff': list(self.buff_eff.values()),
            'inf_pos': self.inf_pos,
            'posture': self.posture,
            'cover': self.cover,
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
            winner: GamePlayer = self.end_check()
            if winner is not None:
                self.batch_sending('endm', None, winner)
                exec(self.match_config['match_end'])
                return winner
            self.batch_sending('endg', None, pl[0])
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
        # 连锁计数
        self.react_times = 0
        self.winner: GamePlayer = None
        self.win_reason = 0
        self.start_time = datetime.now()
        self.loser: GamePlayer = None

        self.turn_process = self.game_config['turn_process']
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

        process = self.game_config['process']
        for ph in process:
            self.enter_phase(ph)
            if self.winner is not None:
                self.loser = self.players[self.winner.sp]
                break
        return self.winner, self.loser

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
            self.__end_phase(ETimePoint.PH_MULLIGAN_END)
        elif ph == EGamePhase.PLAY_CARD:
            self.__enter_phase(ETimePoint.PH_PLAY_CARD)
            self.__ph_play_card()

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
            shown_card_index = p.input(check_ind, 'req_chs_tgt_f',
                                       [card_vid, 1])

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
            for c in p.hand:
                c.ATK.add_val = randint(-2, 2) * 500
                self.enter_time_point(TimePoint(ETimePoint.EXTRA_DATA_GENERATING, None, c))
            # 调查筹码
            i = randint(0, len(p.hand) - 1)
            p.hand[i].ATK.add_val = 0
            p.hand[i].register_effect(EffInvestigator(p.hand[i]), True)
            self.enter_time_point(TimePoint(ETimePoint.INVESTIGATOR_GENERATED, None, p.hand[i]))

        gen(self.p1)
        gen(self.p2)

        self.enter_time_point(TimePoint(ETimePoint.EXTRA_DATA_GENERATED))
        # 用处是传输。
        self.p1.shuffle()
        self.p2.shuffle()

        self.batch_sending('lst_all_ano')

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
                # 影响力值发挥作用后归零，成为附加值。
                card.ATK.add_val = 0
                self.batch_sending('go', [x, y, card.vid], p)

                # 放下后的处理。
                self.enter_time_point(TimePoint(ETimePoint.CARD_PUT, None, [x, y, card]))
                return True
        f = True
        while f:
            f = go(self.p1) | go(self.p2)
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
            # 将卡取走。
            if d:
                cards = [self.chessboard[self.scale * y + x],
                         self.chessboard[self.scale * y + x + d]]
                self.chessboard[self.scale * y + x] = None
                self.chessboard[self.scale * y + x + d] = None
            else:
                cards = [self.chessboard[self.scale * y + x]]
                self.chessboard[self.scale * y + x] = None
            for card in cards:
                p.hand.append(card)
                card.location = 2 - p.sp + ELocation.HAND
                p.update_vc(card)
            self.batch_sending('tk_crd', [x, y, d], p)
            for card in cards:
                self.enter_time_point(TimePoint(ETimePoint.CARD_TOOK, None, card))

        # 后手玩家在这个环节中先取走卡片以平衡先后手。
        self.exchange_turn()
        f = True
        while f:
            f = False

            take_card(self.turn_player)
            self.exchange_turn()

            for c in self.chessboard:
                f = f | (c is not None)
        self.turn_player.shuffle()
        self.op_player.shuffle()

    def __ph_play_card(self):
        def check(*_args):
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
                    _tp = TimePoint(ETimePoint.TRY_SUMMON, None, [_c, _args[2], _args[3], 1])
                    self.enter_time_point(_tp)
                    # 换掉_c的效果不会出，太奇怪了
                    if not _tp.args[-1]:
                        return EErrorCode.FORBIDDEN_SUMMON
                    # 是否还有剩余的入场次数
                    if self.turn_player.summon_times == 0:
                        return EErrorCode.TIMES_LIMIT
                    _tp = TimePoint(ETimePoint.TRIED_SUMMON, None, [_c, _args[2], _args[3], _tp.args[-1]])
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
                        return EErrorCode.FORBIDDEN_STRATEGY
                    # 是否还有剩余的使用次数
                    if self.turn_player.strategy_times == 0:
                        return EErrorCode.TIMES_LIMIT
                    _tp = TimePoint(ETimePoint.TRIED_ACTIVATE_STRATEGY, None, [_c, _tp1.args[-1]])
                    self.enter_time_point(_tp)
                    return 0
                return EErrorCode.UNKNOWN_CARD
            # act 询问可发动的效果
            elif _args[0] == 1:
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
                    if self.turn_player.strategy_times == 0:
                        return EErrorCode.TIMES_LIMIT
                    return 0
                return EErrorCode.UNKNOWN_CARD
            # attack 尝试发动攻击
            elif _args[0] == 3:
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
                    if _c.cover:
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
                        _tp = TimePoint(ETimePoint.TRY_CHANGE_POSTURE, None, [c, 1])
                        self.enter_time_point(_tp)
                        if not _tp.args[-1]:
                            return EErrorCode.FORBIDDEN_CP
                    return 0
                # 策略
                elif _args[1] in range(3, 6):
                    _c = self.turn_player.on_field[_args[1]]
                    if _c is None:
                        return EErrorCode.DONT_EXIST
                    if _c.cover:
                        _tp = TimePoint(ETimePoint.TRY_UNCOVER_STRATEGY, None, [c, 1])
                        self.enter_time_point(_tp)
                        if not _tp.args[-1]:
                            return EErrorCode.FORBIDDEN_UNCOVER
                        return 0
                    return EErrorCode.ALREADY_UNCOVERED
                else:
                    return EErrorCode.OVERSTEP
            else:
                return EErrorCode.INVALID_INPUT

        def check_ind(_ind):
            if _ind not in range(0, _len):
                return EErrorCode.OVERSTEP
            return 0

        # 重置先后手
        self.turn_player = self.p2
        self.op_player = self.p1
        while self.winner is None:
            if self.turns >= 50:
                self.win_reason = 3
                self.judge()
                break
            ntp = self.next_turn_phase()
            self.next_turn(ntp)
            while (self.turn_phase != ETurnPhase.ENDING) & (self.winner is None):
                cmd = list(self.turn_player.input(check, 'req_op'))
                # play card 打出手牌
                if cmd[0] == 0:
                    c = self.turn_player.hand[cmd[1]]
                    # 先消耗次数。
                    if c.type == ECardType.EMPLOYEE:
                        self.turn_player.summon_times -= 1
                        self.summon(self.turn_player, self.turn_player, c, cmd[2], cmd[3])
                    elif c.type == ECardType.STRATEGY:
                        self.turn_player.strategy_times -= 1
                        self.activate_strategy(self.turn_player, self.turn_player, c, cmd[2])
                # act 询问可发动的效果
                elif cmd[0] == 1:
                    efs = list()
                    for c in self.vid_manager.get_cards():
                        # 场上盖放的策略不在这里处理
                        if (self.get_player(c) is self.turn_player) & \
                                (not ((c.type == ECardType.STRATEGY) & (c.location & ELocation.ON_FIELD > 0) &
                                 c.cover)):
                            for ef in c.effects:
                                if (not ef.trigger) and ef.condition(None):
                                    efs.append(ef)
                    _len = len(efs)
                    if _len:
                        self.turn_player.output('req_rct')
                        if self.turn_player.input(lambda yn: 0, 'req_yn'):
                            ef_ind = self.turn_player.free_input(
                                check_ind,
                                'req_chs_eff', [[[ef.host.vid, ef.description] for ef in efs]])
                            # 发动了效果。
                            if ef_ind is not None:
                                self.activate_effect(efs[ef_ind])
                # set 将手牌盖放到场上
                elif cmd[0] == 2:
                    c = self.turn_player.hand[cmd[1]]
                    if c.type == ECardType.EMPLOYEE:
                        self.turn_player.summon_times -= 1
                        self.set_em(self.turn_player, self.turn_player, c, cmd[2])
                    elif c.type == ECardType.STRATEGY:
                        self.turn_player.strategy_times -= 1
                        self.set_strategy(self.turn_player, self.turn_player, c, cmd[2])
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
                    if tp.args[-1] & ((attacker.charge | attacker.turns) > 0):
                        atk_tgt.append(self.op_player.leader.vid)
                    _len = len(atk_tgt)
                    tgt_ind = self.turn_player.free_input(check_ind, 'req_atk', [atk_tgt])
                    if tgt_ind is None:
                        continue
                    tgt = self.vid_manager.get_card(atk_tgt[tgt_ind])
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
                        if c.cover:
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
                            tp = TimePoint(ETimePoint.CHANGING_POSTURE, None, [c, 1])
                            self.batch_sending('crd_cp', [c.vid])
                            self.enter_time_point(tp)
                            if tp.args[-1]:
                                c.posture = not c.posture
                                self.batch_sending('upd_vc', [c.vid, c.serialize()])
                            self.enter_time_point(TimePoint(ETimePoint.CHANGED_POSTURE, None, [c]))
                    elif c.type == ECardType.STRATEGY:
                        self.turn_player.strategy_times -= 1
                        tp = TimePoint(ETimePoint.UNCOVERING_STRATEGY, None, [c, 1])
                        self.enter_time_point(tp)
                        if tp.args[-1]:
                            self.activate_strategy(self.turn_player, self.turn_player, c, cmd[1])
                        self.enter_time_point(TimePoint(ETimePoint.UNCOVERED_EM, None, [c]))

    def next_turn_phase(self):
        for p in self.turn_process:
            yield p

    def enter_turn_phase(self, ph):
        self.batch_sending('ent_tph', [ph], self.turn_player)
        self.turn_phase = ph
        if ph == ETurnPhase.BEGINNING:
            self.enter_time_point(TimePoint(ETimePoint.TURN_BEGIN))
            # 重置次数
            self.__beginning()
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
            self.enter_time_point(TimePoint(ETimePoint.TURN_END))
            # 场上全部卡历经回合数+1
            self.__ending()

    def __beginning(self):
        self.turns += 1
        # 重置可召唤、适用策略次数。
        for p in self.players:
            p.summon_times = 1
            p.strategy_times = 1
            for c in p.on_field:
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
            tp = TimePoint(ETimePoint.TRY_DRAW, None, [count, True])
            self.enter_time_point(tp)
            if tp.args[1]:
                self.draw_card(self.turn_player, tp.args[0])

    def judge(self):
        """
        强制进行单局的胜负判断。
        :return:
        """
        self.winner = self.p1 if self.p1.leader.DEF > self.p2.leader.DEF else self.p2

    def exchange_turn(self):
        p = self.op_player
        self.op_player = self.turn_player
        self.turn_player = p

    def next_turn(self, ntp):
        self.exchange_turn()
        self.enter_turn_phase(ETurnPhase.BEGINNING)
        self.enter_turn_phase(ETurnPhase.DP)
        self.enter_turn_phase(next(ntp))

    def enter_time_point(self, tp: TimePoint, out: bool = True):
        self.tp_stack.append(tp)
        if out:
            self.batch_sending('ent_tp', [tp.tp])
        if tp.sender is None:
            # 先询问对方。
            self.react(self.op_player, tp)
        else:
            self.react(self.players[self.get_player(tp.sender.host).sp], tp)
        self.tp_stack.remove(tp)

    def enter_time_points(self):
        tts = list()
        p = self.turn_player
        for t in self.temp_tp_stack[::-1]:
            self.tp_stack.append(t)
            tts.append(t)
            p = p if t.sender is None else self.get_player(t.sender.host)
            self.batch_sending('ent_tp', [t.tp])
            # 先询问对方。
            self.react(self.players[p.sp], t)

        self.temp_tp_stack.clear()
        # 不需要倒序移除。
        for t in tts:
            self.tp_stack.remove(t)

    def react(self, p: GamePlayer, tp: TimePoint, itor=True):
        """
        询问p是否连锁。先询问对手。
        :param p: 连锁发起者，被最后询问的人。
        :param tp: 询问连锁的时点。
        :param itor: 是否继续迭代
        :return:
        """
        def check_yn(yn):
            return 0

        def check_eff_ind(ind):
            return 0 if ind in range(0, ind_max) else EErrorCode.OVERSTEP

        if p.can_react:
            f = False
            self.react_times += 1
            p_react_list = list()
            for ef in self.ef_listener:
                if ef.condition(tp):
                    if self.get_player(ef.host) is p:
                        if ef.force_exec:
                            self.activate_effect(ef)
                        else:
                            p_react_list.append(ef)
            if len(p_react_list) > 0 or not p.auto_skip:
                p.output('req_rct')
                if p.input(check_yn, 'req_yn'):
                    ind_max = len(p_react_list)
                    p_react_ef_ind = p.free_input(
                        check_eff_ind,
                        'req_chs_eff', [[[ef.host.vid, ef.description] for ef in p_react_list]])
                    if p_react_ef_ind is not None:
                        # 有人连锁，重置可连锁状态
                        for pi in self.players:
                            pi.can_react = 1
                        # 响应了效果。
                        self.activate_effect(p_react_list[p_react_ef_ind])
                        f = True
                else:
                    p.can_react = 0
            if itor | f:
                self.react(self.players[p.sp], tp, False)
            self.react_times -= 1
        # 连锁完成，重置可连锁状态
        if self.react_times == 0:
            for pi in self.players:
                pi.can_react = 1

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

    def activate_effect(self, ef):
        """
        启动效果。(cost+execute)
        :param ef:
        :return:
        """
        if len(self.tp_stack):
            tp = self.tp_stack[-1]
        else:
            tp = None
        if ef.cost(tp):
            if ef.secret:
                ef.execute()
                return
            tp = TimePoint(ETimePoint.PAID_COST, ef, [1])
            self.temp_tp_stack.append(tp)
            self.enter_time_points()
            if tp.args[-1]:
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

    def draw_card(self, p: GamePlayer, count, ef: Effect = None, with_tp=True):
        """
        抽卡。
        :param p: 发动效果的玩家
        :param count: 抽卡数量
        :param ef: 所属效果，为None表示无源效果
        :param with_tp: 能否响应
        :return:
        """
        if with_tp:
            check_point = self.activate_effect_step2(ef, ETimePoint.DRAWING, None, count)
            if next(check_point):
                cs = list()
                for i in range(0, count):
                    if len(p.deck) > 0:
                        c = p.deck.pop()
                        cs.append(c)
                        p.hand.append(c)
                    else:
                        break
                self.enter_time_point(TimePoint(ETimePoint.DRAWN, None, cs))
        else:
            for i in range(0, count):
                if len(p.deck) > 0:
                    p.hand.append(p.deck.pop())
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
                tp = TimePoint(ETimePoint.SUMMONING, ef, [em, pos, posture, 1])
                self.enter_time_point(tp)
                if tp.args[-1]:
                    pos, posture = tp.args[1:3]
                    pt.on_field[pos] = em
                    em.inf_pos = pos
                    em.cover = 0
                    em.posture = (posture == 1)
                    next(cm)
                    # todo: 换em的效果不会出。
                    self.temp_tp_stack.append(TimePoint(ETimePoint.SUCC_SUMMON, ef, [em, pos, posture]))
                    self.batch_sending('upd_vc', [em.vid, em.serialize()])
                    self.batch_sending('smn', [em.vid, int(ef is None)], p)
                    self.enter_time_points()
                    # 重置攻击、阻挡次数
                    em.reset_times()

    def special_summon(self, p: GamePlayer, pt: GamePlayer, em: GameCard, ef: Effect):
        """
        雇员请求特殊入场。
        :param p: 发起召唤的玩家
        :param pt: player target 召唤到
        :param em: 雇员
        :param ef:
        :return:
        """
        def check_pos(_pos):
            if _pos not in range(0, 3):
                return EErrorCode.OVERSTEP
            if pt.on_field[_pos] is not None:
                return EErrorCode.INVALID_PUT
            return 0

        for posture in range(0, 2):
            for pos in range(0, 3):
                if pt.on_field[pos] is None:
                    tp = TimePoint(ETimePoint.TRY_SUMMON, ef, [em, pos, posture, 1])
                    self.enter_time_point(tp)
                    # 入场被允许
                    if tp.args[-1]:
                        # 询问入场位置、姿态
                        pos = p.input(check_pos, 'req_num', [0, 3])
                        if pos is not None:
                            posture = p.input(lambda x: 0, 'req_num', [0, 2]) > 0
                            self.summon(p, pt, em, pos, posture, ef)
                            return
            
    def activate_strategy(self, p: GamePlayer, pt: GamePlayer, s: GameCard, pos):
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
            tp = TimePoint(ETimePoint.ACTIVATING_STRATEGY, None, [s, 1])
            self.enter_time_point(tp)
            # 发动成功
            if tp.args[-1]:
                pt.on_field[pos] = s
                s.inf_pos = pos
                s.cover = 0
                next(cm)
                # todo: 换s的效果不会出。
                self.temp_tp_stack.append(TimePoint(ETimePoint.SUCC_ACTIVATE_STRATEGY, None, s))
                self.batch_sending('upd_vc', [s.vid, s.serialize()])
                self.batch_sending('act_stg', [s.vid], p)
                self.enter_time_points()
                # 策略使用时自动发动效果。
                self.activate_effect(s.effects[0])
                # 非持续/单人策略发动后离场
                if not ((s.subtype & EStrategyType.LASTING) |
                         (s.subtype & EStrategyType.ATTACHMENT)):
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

    def set_strategy(self, p: GamePlayer, pt: GamePlayer, s: GameCard, pos, ef: Effect = None):
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
                pt.on_field[pos] = s
                s.inf_pos = pos
                s.cover = 1
                next(cm)
                for pi in self.players:
                    if pi is p:
                        pi.output('upd_vc', [s.vid, s.serialize()])
                    else:
                        pi.output('upd_vc_ano', [s.vid, s.serialize_anonymous()])
                self.batch_sending('set_crd', [s.vid], p)
                self.enter_time_points()

    def send_to_grave(self, p: GamePlayer, pt: GamePlayer, c: GameCard, ef: Effect = None):
        """
        送去墓地。
        :param p:
        :param pt: 送去目标玩家的墓地。
        :param c:
        :param ef:
        :return:
        """
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

    def deal_damage(self, sender: GameCard, target: GameCard, damage: int, ef: Effect = None):
        """
        造成伤害。
        :param sender: 伤害来源。
        :param target: 目标。
        :param damage: 伤害量。
        :param ef:
        :return:
        """
        tp = TimePoint(ETimePoint.DEALING_DAMAGE, ef, [sender, target, damage, 1])
        self.enter_time_point(tp)
        if tp.args[-1]:
            sender, target, damage = tp.args[:-1]
            # gain会通知客户端。
            target.DEF.gain(-damage)
            # todo: 是特性，不是bug。
            self.batch_sending('dmg', [target.vid, damage], self.get_player(sender))
            self.enter_time_point(TimePoint(ETimePoint.DEALT_DAMAGE, ef, [sender, target, damage]))

    def destroy(self, sender: GameCard, target: GameCard, ef: Effect = None):
        """
        摧毁指定的卡。
        :param sender: 摧毁者。
        :param target: 被摧毁的目标卡。
        :param ef:
        :return:
        """
        tp = TimePoint(ETimePoint.DESTROYING, ef, [sender, target, 1])
        self.enter_time_point(tp)
        if tp.args[-1]:
            sender, target = tp.args[:-1]
            if target.type == ECardType.LEADER:
                self.winner = self.players[self.get_player(target).sp]
                self.win_reason = 0
            else:
                # todo: 是特性，不是bug。
                self.batch_sending('crd_des', [target.vid], self.get_player(sender))
                self.send_to_grave(self.get_player(sender), self.get_player(target), target, ef)
                self.enter_time_point(TimePoint(ETimePoint.DESTROYED, ef, [sender, target]))

    def choose_target(self, func, ef: Effect, force=False, with_tp=True) -> GameCard:
        """
        选择效果目标。效果的host(宿主)一定是效果的发动者。
        :param func:  筛选函数。
        :param ef:
        :param force: 是否强制
        :param with_tp:
        :return:
        """
        def check_ind(_ind):
            if _ind not in range(0, _len):
                return EErrorCode.OVERSTEP
            return 0

        cs = list()
        if with_tp:
            for c in self.vid_manager.get_cards():
                if func(c):
                    # 模拟选择。
                    tp = TimePoint(ETimePoint.TRY_CHOOSE_TARGET, ef, [c, 1])
                    self.enter_time_point(tp)
                    if tp.args[-1]:
                        cs.append(c.vid)
            _len = len(cs)
            # 询问选项
            if force:
                ind = self.get_player(ef.host).input(check_ind, 'req_chs_tgt_f', [cs, 1])
            else:
                ind = self.get_player(ef.host).free_input(check_ind, 'req_chs_tgt_f', [cs, 1])
                if ind is None:
                    return None
            c = self.vid_manager.get_card(cs[ind])
            tp = TimePoint(ETimePoint.CHOOSING_TARGET, ef, [c, 1])
            self.enter_time_point(tp)
            if tp.args[-1]:
                self.enter_time_point(TimePoint(ETimePoint.CHOSE_TARGET, ef, [c]))
                return c
        else:
            for c in self.vid_manager.get_cards():
                if func(c):
                    cs.append(c.vid)
            _len = len(cs)
            # 询问选项
            if force:
                ind = self.get_player(ef.host).input(check_ind, 'req_chs_tgt_f', [cs, 1])
            else:
                ind = self.get_player(ef.host).free_input(check_ind, 'req_chs_tgt_f', [cs, 1])
                if ind is None:
                    return None
            return self.vid_manager.get_card(cs[ind])
        return None
