from utils.constants import ECardRank, ECardType, ELocation, ETimePoint,\
    EGamePhase  # , EInOperation, EOutOperation
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
        self.graveyard = list()
        # 除外区
        self.exiled = list()
        # 场上
        self.in_field = list()
        self.leader: GameCard = None
        self.leader_id = leader_card_id
        # 是否为先手玩家。
        self.sp = 0

    def init_game(self, g, p_loc: ELocation):
        self.game_now = g

        self.sp = int(g.p1 == self)
        self.leader = GameCard(g, self.leader_id, ELocation.UNKNOWN)
        hd = list()
        sd = list()
        for cid in self.ori_deck.keys():
            for i in range(self.ori_deck[cid][0]):
                if int(self.ori_deck[cid][3]):
                    gc = GameCard(g, cid, ELocation.SIDE.value + p_loc.value)
                    # self.vision.append(gc.vid)
                    sd.append(gc)
                else:
                    gc = GameCard(g, cid, ELocation.HAND.value + p_loc.value)
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
            p.output('shf', [loc.value + 2 - self.sp])
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
        self.type = ECardType(int(rds.hget(cid, 'type').decode()))
        self.subtype = int(rds.hget(cid, 'subtype').decode())
        self.rank = ECardRank(int(rds.hget(cid, 'rank').decode()))
        self.src_atk = int(rds.hget(cid, 'atk_eff').decode())
        self.src_def = int(rds.hget(cid, 'def_hp').decode())
        self.series = json.loads(rds.hget(cid, 'series').decode())
        # 附加值。additional value
        self.add_val = 0
        # basic atk/def = source atk/def + add_val, 用于倍乘、变成XXX
        self.bsc_atk = self.src_atk  # + self.add_val
        self.buff_atk = 0
        self.buff_def = 0
        self.halo_atk = 0
        self.halo_def = 0
        self.is_token = is_token
        self.effects = list()
        self.location = ori_loc
        # 在对局中获得的效果。{eff: desc}
        self.buff_eff = dict()
        # in field position 在自己场上的位置。0-2: 雇员区 3-5: 策略区
        self.inf_pos = 0
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
        self.bsc_atk = self.src_atk + self.add_val
        self.buff_atk = 0
        self.buff_def = 0
        self.halo_atk = 0
        self.halo_def = 0
        for e in self.effects:
            if not e.no_reset:
                self.remove_effect(e)
        m = import_module('cards.c{}.py'.format(self.cid))
        m.give(self)

    def serialize(self):
        return {
            'vid': self.vid,
            'cid': self.cid,
            'name': self.name,
            'type': self.type.value,
            'subtype': self.subtype,
            'rank': self.rank.value,
            'src_atk': self.src_atk,
            'src_def': self.src_def,
            'series': self.series,
            'add_val': self.add_val,
            'bsc_atk': self.bsc_atk,
            'buff_atk': self.buff_atk,
            'buff_def': self.buff_def,
            'halo_atk': self.halo_atk,
            'halo_def': self.halo_def,
            'is_token': self.is_token,
            'location': self.location,
            'buff_eff': list(self.buff_eff.values()),
            'inf_pos': self.inf_pos
                           }

    def serialize_anonymous(self):
        return {
            'vid': self.vid,
            'add_val': self.add_val,
            'location': self.location,
            'buff_eff': list(self.buff_eff.values()),
            'inf_pos': self.inf_pos
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
    def __init__(self, tp_id: ETimePoint, sender: Effect = None, args=None):
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
        self.batch_sending('startm', None)
        exec(self.match_config["match_init"])
        last_loser = None
        while True:
            self.game_now = Game(self.players, self.match_config["game_config"], last_loser)
            pl: tuple = self.game_now.start()
            self.wins[pl[0]] += 1
            last_loser = pl[1]
            winner: GamePlayer = self.end_check()
            if winner is not None:
                self.batch_sending('endm', winner)
                exec(self.match_config['match_end'])
                return winner
            self.batch_sending('endg', pl[0])
            self.batch_sending('mbreak', None)
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

    def batch_sending(self, op, sender, args: list = None):
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

        # 放置&取走阶段时用的6*6棋盘
        self.chessboard = [None for x in range(0, 36)]
        # 当前回合数
        self.turns = 1
        self.game_config = game_config
        self.last_loser = last_loser
        self.phase_now: EGamePhase = None
        self.winner: GamePlayer = None
        self.loser: GamePlayer = None

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
            ph = EGamePhase(ph)
            self.enter_phase(ph)
            if self.winner is not None:
                break
        return self.winner, self.loser

    def enter_phase(self, ph: EGamePhase):
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

    def __enter_phase(self, tp: ETimePoint):
        self.enter_time_point(TimePoint.generate(tp), False)
        self.batch_sending('ent_ph', None, [self.phase_now.value])

    def __end_phase(self, tp):
        self.enter_time_point(TimePoint.generate(tp), False)
        self.batch_sending('endp', None, [tp.value])

    def __ph_sp_decide(self):
        a = randint(1, 16)
        if a > 8:
            self.p1 = self.players[0]
            self.p2 = self.players[1]
        else:
            self.p1 = self.players[1]
            self.p2 = self.players[0]
        # 输出
        self.batch_sending('sp_decided', self.p1)

        self.turn_player = self.p1
        self.op_player = self.p2

        self.p1.init_game(self, ELocation.P1)
        self.p2.init_game(self, ELocation.P2)

        self.p1.init_card_info()
        self.p2.init_card_info()

    def __ph_show_card(self):
        def show_one(p: GamePlayer, rank: ECardRank):
            def check_ind(ind):
                return ind in range(0, ind_max)

            p.output('req_shw_crd', [rank.value])

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
                c.add_val = randint(-2, 2) * 500
                self.enter_time_point(TimePoint(ETimePoint.EXTRA_DATA_GENERATING, None, c))
            # 调查筹码
            i = randint(0, 17)
            p.hand[i].add_val = 0
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
                return _x in range(0, 6) and _y in range(0, 6) and\
                       self.chessboard[_y * 6 + _x] is None and _ind < ind_max

            hand = p.hand
            if len(hand) == 0:
                return False
            else:
                card_vid = [c.vid for c in hand]
                ind_max = len(hand)
                # x, y, ind
                x, y, ind = p.input(check_go, 'req_go', [card_vid])
                c = self.vid_manager.get_card(card_vid[ind])
                self.chessboard[y * 6 + x] = c
                hand.remove(c)
                # 变化周围的数值。
                cs = adj_pos(x, y)
                for ac in cs:
                    if self.chessboard[ac] is not None:
                        self.chessboard[ac].add_val += c.add_val
                # 影响力值发挥作用后归零，成为附加值。
                c.add_val = 0
                self.batch_sending('go', p, [x, y, card_vid[ind]])

                # 放下后的处理。
                self.enter_time_point(TimePoint(ETimePoint.CARD_PUT, None, [x, y, c]))
                return True
        f = True
        while f:
            f = go(self.p1) | go(self.p2)
        self.enter_time_point(TimePoint(ETimePoint.EXTRA_DATA_CALC))
        # todo: del
        p1s = 0
        p2s = 0
        for c in self.p1.hand:
            p1s += c.add_val
        for c in self.p2.hand:
            p2s += c.add_val
        self.winner = self.p1 if p1s > p2s else self.p2

    def __ph_take_card(self):
        
        self.p1.shuffle()
        self.p2.shuffle()

    def exchange_turn(self):
        p = self.op_player
        self.op_player = self.turn_player
        self.turn_player = p

    # def next_turn(self):
    #     self.turns += 1
    #     self.exchange_turn()

    def enter_time_point(self, tp: TimePoint, out: bool = True):
        self.tp_stack.append(tp)
        if out:
            self.batch_sending('ent_tp', None, [tp.tp.value])
        self.react()
        self.tp_stack.remove(tp)

    def enter_time_points(self):
        tts = list()
        mtts = list()
        for t in self.temp_tp_stack:
            self.tp_stack.append(t)
            tts.append(t)
            mtts.append(t.tp.value)

        self.batch_sending('ent_tp', None, [*mtts])

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
            return yn == 1 or yn == 0

        def check_eff_ind(ind):
            return ind in range(0, ind_max)

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

    def batch_sending(self, op, sender=None, args: list = None):
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

    # -------⬇效果函数(execute部分)⬇--------
    def activate_effect_step2(self, ef: Effect, doing_tp: ETimePoint, done_tp: ETimePoint,
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
            doing_tp = TimePoint(doing_tp, ef, args)
            self.enter_time_point(doing_tp)
        if ef is None:
            yield
            if done_tp is not None:
                done_tp = TimePoint(done_tp, None, args)
                self.enter_time_point(done_tp)
        elif ef.succ_activate:
            yield
            if done_tp is not None:
                done_tp = TimePoint(done_tp, ef, args)
                self.enter_time_point(done_tp)
        yield

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
            next(check_point)
            self.batch_sending('upd_vc', p, [vid, self.vid_manager.get_card(vid).serialize()])
            self.batch_sending('shw_crd', p, [vid])
            next(check_point)
        else:
            self.batch_sending('upd_vc', p, [vid, self.vid_manager.get_card(vid).serialize()])
            self.batch_sending('shw_crd', p, [vid])
