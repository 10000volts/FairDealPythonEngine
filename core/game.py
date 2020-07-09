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
        self.game_now = None

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

    def init_game(self, g, p_loc):
        self.game_now = g

        self.sp = int(g.p1 == self)
        self.leader = GameCard(g, self.leader_id, ELocation.UNKNOWN)
        hd = list()
        sd = list()
        for cid in self.ori_deck.keys():
            for i in range(self.ori_deck[cid][0]):
                if int(self.ori_deck[cid][3]):
                    gc = GameCard(g, cid, ELocation.SIDE + p_loc)
                    # self.vision.append(gc.vid)
                    sd.append(gc)
                else:
                    gc = GameCard(g, cid, ELocation.HAND + p_loc)
                    # self.vision.append(gc.vid)
                    hd.append(gc)
        self.deck = list()
        self.ori_side = sd
        self.side = sd
        # 手牌
        self.hand = hd

    def input(self, func, *args):
        return self.in_method(self, make_input(*args), func)

    def output(self, *args):
        msg = make_output(*args)
        # 与之对应，输入不需要记录。
        if self.game_now is not None:
            self.game_now.record(self, msg)
        self.out_method(self.upstream, msg)

    def init_card_info(self):
        """
        向客户端发送初始化卡片请求。
        :return:
        """
        for c in self.hand:
            self.update_vc(c)
        for p in self.game_now.players:
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
            self.game_now.vid_manager.change(c.vid)
        # g: Game = self.game_now
        for p in self.game_now.players:
            p.output('shf', [loc + 2 - self.sp])
            if p == self:
                for c in self.hand:
                    self.update_vc(c)
            else:
                for c in self.hand:
                    p.update_vc_ano(c)

    def update_vc(self, c):
        self.output('upd_vc', [c.vid, c.serialize()])

    def update_vc_ano(self, c):
        self.output('upd_vc_ano', [c.vid, c.serialize_anonymous()])


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
        self.op_st = list()
        # 数值栈。
        self.val_st = list()
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
                v += getattr(x, 'x')()
            elif (op == '*x') | (op == '**x'):
                x = self.val_st[i]
                v *= getattr(x, 'x')()
            elif (op == '=x') | (op == '==x'):
                x = self.val_st[i]
                v = getattr(x, 'x')()
            i += 1
        self.value = v if v > 0 else 0
        t1 = TimePoint(self.tp1, None, self.value)
        self.card.game.enter_time_point(t1)
        self.value = int(t1.args) if t1.args > 0 else 0
        self.card.game.enter_time_point(TimePoint(self.tp2, None, self.value))

    def gain(self, v, perm: bool):
        """
        攻击力上升/下降。
        :param v:
        :param perm: 是否永久。
        :return:
        """
        self.op_st.append('++' if perm else '+')
        self.val_st.append(v)
        self.update()

    def gain_x(self, x, perm: bool):
        self.op_st.append('++x' if perm else '+x')
        self.val_st.append(x)
        self.update()

    def become(self, v, perm: bool):
        self.op_st.append('==' if perm else '=')
        self.val_st.append(v)
        self.update()

    def become_x(self, x, perm: bool):
        self.op_st.append('==x' if perm else '=x')
        self.val_st.append(x)
        self.update()

    def ratio(self, v, perm: bool):
        self.op_st.append('**' if perm else '*')
        self.val_st.append(v)
        self.update()

    def ration_x(self, x, perm: bool):
        self.op_st.append('**x' if perm else '*x')
        self.val_st.append(x)
        self.update()


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
        self.DEF = CardProperty(self.src_def, ETimePoint.DEF_CALCING, ETimePoint.DEF_CALC, self)
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
        m = import_module('cards.c{}'.format(self.cid))
        m.give(self)

    def register_effect(self, e: Effect, buff_eff=False):
        """

        :param e:
        :param buff_eff: 是否是附加的效果。
        :return:
        """
        self.effects.append(e)
        if buff_eff:
            self.buff_eff[e] = e.description

    def remove_effect(self, e):
        self.effects.remove(e)
        if e in self.buff_eff:
            self.buff_eff.pop(e)
        if e in self.game.ef_listener:
            self.game.ef_listener.remove(e)

    def reset(self):
        """
        离场时，清除所有非永久的buff，效果复原。
        :return:
        """
        for e in self.effects:
            if not e.no_reset:
                self.remove_effect(e)
        m = import_module('cards.c{}.py'.format(self.cid))
        m.give(self)
        self.ATK.reset()
        self.DEF.reset()

    def move_to(self, ef, loc):
        """
        移动至另一个区域。不能单独使用(但移动区域时必须调用)，不会触发时点。
        :param ef: effect
        :param loc:
        :return:
        """
        if (loc & self.location) == 0:
            p = self.game.players[(self.location & ELocation.P1) == 0]

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

            def enter():
                if loc & ELocation.HAND:
                    return ETimePoint.IN_HAND, ETimePoint.IN_HAND_END, p.hand
                if loc & ELocation.DECK:
                    return ETimePoint.IN_DECK, ETimePoint.IN_DECK_END, p.deck
                if loc & ELocation.SIDE:
                    return ETimePoint.IN_SIDE, ETimePoint.IN_SIDE_END, p.side
                if loc & ELocation.ON_FIELD:
                    return ETimePoint.IN_FIELD, ETimePoint.IN_FIELD_END, p.on_field
                if loc & ELocation.GRAVE:
                    return ETimePoint.IN_GRAVE, ETimePoint.IN_GRAVE_END, p.grave
                if loc & ELocation.EXILED:
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
            # 进入, 入场不在这里处理
            if self.location & ELocation.ON_FIELD == 0:
                _from.append(self)
            tp3 = TimePoint(etp3, ef, self)
            tp4 = TimePoint(etp3, ef, self)
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
            'posture': self.posture
                           }

    def serialize_anonymous(self):
        return {
            'vid': self.vid,
            'add_val': self.ATK.add_val,
            'location': self.location,
            'buff_eff': list(self.buff_eff.values()),
            'inf_pos': self.inf_pos,
            'posture': self.posture
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
        self.game_now = None

        self.wins = {gp1: 0, gp2: 0}

    def start(self):
        self.batch_sending('startm')
        exec(self.match_config["match_init"])
        last_loser = None
        while True:
            self.game_now = Game(self.players, self.match_config["game_config"], last_loser)
            pl: tuple = self.game_now.start()
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
            p.output(op, args, True if sender is None else p == sender)


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
        self.players = players
        # 先手玩家代表
        self.p1: GamePlayer = None
        # 后手玩家代表
        self.p2: GamePlayer = None
        # 进行当前回合的玩家代表
        self.turn_player: GamePlayer = None
        # 未进行当前回合的玩家代表
        self.op_player: GamePlayer = None

        # 棋盘规模。
        self.scale = self.game_config['scale']
        # 放置&取走阶段时用的6*6棋盘
        self.chessboard = [None for x in range(0, self.scale ** 2)]
        # 当前回合数
        self.turns = 0
        self.turn_phase = None
        self.game_config = game_config
        self.last_loser = last_loser
        self.phase_now = None
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
                self.loser = self.players[1 - self.winner.sp]
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

        self.p1.init_game(self, ELocation.P1)
        self.p2.init_game(self, ELocation.P2)

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
            i = randint(0, len(p.hand))
            p.hand[i].ATK.add_val = 0
            p.hand[i].register_effect(EffInvestigator(p, p.hand[i]), True)
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
                p.output('upd_vc', [card.vid, card.serialize()])
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
                    if _args[2] not in range(0, 3) or self.turn_player.on_field[_args[2]] is not None:
                        return EErrorCode.INVALID_PUT
                    _tp = TimePoint(ETimePoint.TRY_SUMMON, None, [_c, _args[3], 1])
                    self.enter_time_point(_tp)
                    if not _tp.args[-1]:
                        return EErrorCode.FORBIDDEN_SUMMON
                    # 是否还有剩余的入场次数
                    if self.turn_player.summon_times == 0:
                        return EErrorCode.TIMES_LIMIT
                    _tp = TimePoint(ETimePoint.TRIED_SUMMON, None, [_c, _tp.args[-1]])
                    self.enter_time_point(_tp)
                    return 0
                elif _c.type == ECardType.STRATEGY:
                    # 不在策略区域或该区域已有策略
                    if _args[2] not in range(3, 6) or self.turn_player.on_field[_args[2]] is not None:
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
                    if not(_tp1.args[-1] & _tp2.args[-1] & _c.effects[0].condition()):
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
                    if _args[2] not in range(0, 3) or self.turn_player.on_field[_args[2]] is not None:
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
                    if _args[2] not in range(3, 6) or self.turn_player.on_field[_args[2]] is not None:
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
                _tp = TimePoint(ETimePoint.TRY_ATTACK, None, [_c, 1])
                self.enter_time_point(_tp)
                if not _tp.args[-1]:
                    return EErrorCode.FORBIDDEN_ATTACK
                return 0
            # next phase 主动进行自己回合的下个阶段
            elif _args[0] == 4:
                return 0
            # 单局认输
            elif _args[0] == 5:
                return 0
            else:
                return EErrorCode.INVALID_INPUT

        while self.winner is None:
            if self.turns >= 50:
                self.win_reason = 3
                self.judge()
                break
            ntp = self.next_turn_phase()
            self.next_turn(ntp)
            while self.turn_phase != ETurnPhase.ENDING:
                cmd = self.turn_player.input(check, 'req_op')
                # play card 打出手牌
                if cmd[0] == 0:
                    c = self.turn_player.hand[cmd[1]]
                    # 先消耗次数。
                    if c.type == ECardType.EMPLOYEE:
                        self.turn_player.summon_times -= 1
                        self.summon(self.turn_player, c, cmd[2], cmd[3], None, True,
                                    self.turn_player.hand, ETimePoint.OUT_HAND, ETimePoint.OUT_HAND_END)
                    elif c.type == ECardType.STRATEGY:
                        self.turn_player.strategy_times -= 1
                        self.activate_strategy(self.turn_player, c, cmd[2], True,
                                               self.turn_player.hand,
                                               ETimePoint.OUT_HAND, ETimePoint.OUT_HAND_END)
                # act 询问可发动的效果
                elif cmd[0] == 1:
                    pass
                # set 将手牌盖放到场上
                elif cmd[0] == 2:
                    c = self.turn_player.hand[cmd[1]]
                    if c.type == ECardType.EMPLOYEE:
                        self.turn_player.summon_times -= 1
                        self.set_em(self.turn_player, c, cmd[2], None, True,
                                    self.turn_player.hand, ETimePoint.OUT_HAND, ETimePoint.OUT_HAND_END)
                    elif c.type == ECardType.STRATEGY:
                        self.turn_player.strategy_times -= 1
                        self.set_strategy(self.turn_player, c, cmd[2], None, True,
                                          self.turn_player.hand,
                                          ETimePoint.OUT_HAND, ETimePoint.OUT_HAND_END)
                # attack 尝试发动攻击
                elif cmd[0] == 3:
                    pass
                # next phase 主动进行自己回合的下个阶段(主要阶段1->战斗阶段1(->战斗阶段2)->主要阶段2->回合结束)
                elif cmd[0] == 4:
                    self.enter_turn_phase(next(ntp))
                # give up 单局认输
                elif cmd[0] == 5:
                    self.win_reason = 2
                    self.winner = self.op_player
                    break

    def next_turn_phase(self):
        for p in self.turn_process:
            yield p

    def enter_turn_phase(self, ph):
        self.batch_sending('ent_tph', [ph], self.turn_player)
        self.turn_phase = ph
        if ph == ETurnPhase.BEGINNING:
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
            self.enter_time_point(TimePoint(ETimePoint.TURN_END))

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
        self.turns += 1
        self.exchange_turn()
        # 重置可召唤、适用策略次数。
        for p in self.players:
            p.summon_times = 1
            p.strategy_times = 1
        self.enter_turn_phase(ETurnPhase.BEGINNING)
        self.enter_turn_phase(ETurnPhase.DP)
        self.enter_turn_phase(next(ntp))

    def enter_time_point(self, tp: TimePoint, out: bool = True):
        self.tp_stack.append(tp)
        if out:
            self.batch_sending('ent_tp', [tp.tp])
        self.react()
        self.tp_stack.remove(tp)

    def enter_time_points(self):
        tts = list()
        for t in self.temp_tp_stack:
            self.tp_stack.append(t)
            tts.append(t)

        self.batch_sending('ent_tp', [[t.tp for t in tts]])

        self.temp_tp_stack.clear()
        self.react()
        # 不需要倒序移除。
        for t in tts:
            self.tp_stack.remove(t)

    def react(self):
        """
        询问连锁。先询问对手。
        :return:
        """
        def check_yn(yn):
            return 0

        def check_eff_ind(ind):
            return 0 if ind in range(0, ind_max) else EErrorCode.OVERSTEP

        op_react_list = list()
        tr_react_list = list()
        for ef in self.ef_listener:
            if ef.condition():
                if ef.owner == self.op_player:
                    if ef.force_exec:
                        self.activate_effect(ef)
                    else:
                        op_react_list.append(ef)
                else:
                    if ef.force_exec:
                        self.activate_effect(ef)
                    else:
                        tr_react_list.append(ef)
        if len(op_react_list) > 0 or not self.op_player.auto_skip:
            self.op_player.output('qry_rct')
            if self.op_player.input(check_yn, 'chs_yn'):
                ind_max = len(op_react_list)
                op_react_ef_ind = self.op_player.input(
                    check_eff_ind,
                    'chs_eff', [[[ef.host.vid, ef.description] for ef in op_react_list]])
                if op_react_ef_ind is not None:
                    # 对方响应了效果。
                    self.activate_effect(op_react_list[op_react_ef_ind])
        if len(tr_react_list) > 0 or not self.turn_player.auto_skip:
            self.turn_player.output('qry_rct')
            if self.turn_player.input(check_yn, 'chs_yn'):
                ind_max = len(tr_react_list)
                tr_react_ef_ind = self.turn_player.input(
                    check_eff_ind,
                    'chs_eff', [[[ef.host.vid, ef.description] for ef in tr_react_list]])
                if tr_react_ef_ind is not None:
                    # 回合持有者响应了效果。
                    self.activate_effect(tr_react_list[tr_react_ef_ind])

    def activate_effect(self, ef):
        """
        启动效果。(cost+execute)
        :param ef:
        :return:
        """
        ef.cost()
        if ef.secret:
            ef.execute()
            return
        self.temp_tp_stack.append(TimePoint(ETimePoint.PAID_COST))
        self.enter_time_points()
        if ef.succ_activate:
            ef.execute()
            self.temp_tp_stack.append(TimePoint(ETimePoint.SUCC_EFFECT_ACTIVATE))
        else:
            self.temp_tp_stack.append(TimePoint(ETimePoint.FAIL_EFFECT_ACTIVATE))
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
            p.output(op, args, True if sender is None else p == sender)

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
                              args=None):
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
            if ef is None:
                yield True
                if done_tp is not None:
                    done_tp = TimePoint(done_tp, None, args)
                    self.enter_time_point(done_tp)
            elif ef.succ_activate:
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
            self.batch_sending('upd_vc', [vid, self.vid_manager.get_card(vid).serialize()], p)
            self.batch_sending('shw_crd', [vid], p)
            next(check_point)
        else:
            self.batch_sending('upd_vc', [vid, self.vid_manager.get_card(vid).serialize()], p)
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

    def summon(self, p: GamePlayer, em: GameCard, pos, posture, ef: Effect = None):
        """
        雇员入场。
        :param p:
        :param em: 雇员
        :param pos: 入场位置(0-2)
        :param posture: 入场姿态(非零表示防御姿态)
        :param ef:
        :return:
        """
        cm = em.move_to(ef, ELocation.ON_FIELD)
        if next(cm):
            self.enter_time_points()
            if next(cm):
                tp = TimePoint(ETimePoint.SUMMONING, ef, [em, 1])
                self.enter_time_point(tp)
                if tp.args[1]:
                    p.on_field[pos] = em
                    em.posture = (posture == 1)
                    next(cm)
                    self.temp_tp_stack.append(TimePoint(ETimePoint.SUCC_SUMMON, ef, em))
                    self.batch_sending('upd_vc', [em.vid, em.serialize()])
                    self.batch_sending('smn', [em.vid, pos, int(ef is None)], p)
                    self.enter_time_points()
            
    def activate_strategy(self, p: GamePlayer, s: GameCard, pos):
        """
        发动策略。
        :param p: 
        :param s: 
        :param pos:
        :return: 
        """
        cm = s.move_to(None, ELocation.ON_FIELD)
        next(cm)
        self.enter_time_points()
        if next(cm):
            tp = TimePoint(ETimePoint.ACTIVATING_STRATEGY, None, [s, 1])
            self.enter_time_point(tp)
            # 发动成功
            if tp.args[1]:
                p.on_field[pos] = s
                next(cm)
                self.temp_tp_stack.append(TimePoint(ETimePoint.SUCC_ACTIVATE_STRATEGY, None, s))
                self.batch_sending('upd_vc', [s.vid, s.serialize()])
                self.batch_sending('act_stg', [s.vid, pos], p)
                self.enter_time_points()
                # 策略使用时自动发动效果。
                self.activate_effect(s.effects[0])
                # 非持续/单人策略发动后离场
                if not ((s.subtype & EStrategyType.LASTING) |
                        (s.subtype & EStrategyType.ATTACHMENT)):
                    cm = s.move_to(None, ELocation.GRAVE)
                    next(cm)
                    self.enter_time_point(tp)
                    if next(cm):
                        p.on_field[pos] = None
                        p.grave.append(s)
                        next(cm)
                        self.enter_time_points()

    def set_em(self, p: GamePlayer, em: GameCard, pos, ef: Effect = None):
        """
        盖放秘密雇员。
        :param p:
        :param em:
        :param pos:
        :param ef:
        :return:
        """
        cm = em.move_to(None, ELocation.ON_FIELD)
        next(cm)
        self.enter_time_points()
        if next(cm):
            tp = TimePoint(ETimePoint.SET_EM, ef, [em, 1])
            self.enter_time_point(tp)
            if tp.args[1]:
                p.on_field[pos] = em
                next(cm)
                self.batch_sending('set', [em.vid, pos], p)
                self.enter_time_points()

    def set_strategy(self, p: GamePlayer, s: GameCard, pos, ef: Effect = None):
        """
        盖放策略。
        :param p:
        :param s:
        :param pos:
        :param ef:
        :return:
        """
        cm = s.move_to(None, ELocation.ON_FIELD)
        next(cm)
        self.enter_time_points()
        if next(cm):
            tp = TimePoint(ETimePoint.SET_STRATEGY, ef, [s, 1])
            self.enter_time_point(tp)
            if tp.args[1]:
                p.on_field[pos] = s
                next(cm)
                self.batch_sending('set', [s.vid, pos], p)
                self.enter_time_points()

    def send_to_grave(self, p: GamePlayer, c: GameCard, ef: Effect = None):
        """
        送去墓地。
        :param p:
        :param c:
        :param ef:
        :return:
        """
        cm = c.move_to(ef, ELocation.GRAVE)
        next(cm)
        self.enter_time_points()
        if next(cm):
            next(cm)
            self.batch_sending('crd_snd2grv', [c.vid], p)
            self.enter_time_points()
