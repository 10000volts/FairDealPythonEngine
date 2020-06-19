from utils.constants import ECardRank, ECardType, ELocation, ETimePoint,\
    EGamePhase  # , EInOperation, EOutOperation
from models.player import Player
from core.io import input_from_socket, input_from_local, input_from_ai, output_2_socket,\
    output_2_local, output_2_ai, set_socket, make_output, make_input
from models.effect import Effect

import random
import redis
import json

# redis键值对int/str不敏感
rds = redis.StrictRedis(db=0)


class GamePlayer:
    """
    游戏中的玩家。
    """
    def __init__(self, p: Player, deck: dict, leader_card_id: int):
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
        # 场上雇员
        self.employees = list()
        # 场上策略
        self.strategy = list()
        self.leader: GameCard = None
        self.leader_id = leader_card_id

    def init_deck(self, g):
        self.leader = GameCard(g, self.leader_id, ELocation.UNKNOWN)
        md = list()
        sd = list()
        for cid in self.ori_deck.keys():
            for i in range(self.ori_deck[cid][0]):
                if int(self.ori_deck[cid][3]):
                    gc = GameCard(g, cid, ELocation.DECK.value)
                    sd.append(gc)
                else:
                    gc = GameCard(g, cid, ELocation.SIDE.value)
                    md.append(gc)
        self.deck = list()
        self.ori_side = sd
        self.side = sd
        # 手牌
        self.hand = md

    def input(self, g, func, *args):
        return self.in_method(self.upstream, g, make_input(*args), func)

    def output(self, *args):
        self.out_method(self.upstream, make_output(*args))

    def init_card_info(self, pl: list):
        """
        向客户端发送初始化卡片请求。
        :param pl: 其他玩家，他们的卡将被初始化成未知卡(知晓存在但不知内容)。
        :return:
        """
        msgs = list()
        for c in self.hand:
            self.update_card(c.gcid, c.serialize())
        for p in pl:
            for c in p.hand:
                self.update_card(c.gcid, None)

    def update_card(self, gcid, info: str):
        self.output('upd_crd', [gcid, info])


class GameCard:
    def __init__(self, g, cid, ori_loc, is_token=False):
        """

        :param cid:
        :param ori_loc: 初始位置。
        :param is_token:
        """
        # game card id
        self.gcid = 0
        g.gcid_manager.register(self)
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
        # basic atk/def = source atk/def + add_val, 用于倍乘
        self.bsc_atk = self.src_atk
        self.buff_atk = 0
        self.buff_def = 0
        self.halo_atk = 0
        self.halo_def = 0
        self.is_token = is_token
        self.effects = list()
        self.location = ori_loc
        # 在对局中获得的效果。{description: effect, ...}
        self.buff_eff = dict()

    def register_effect(self, e: Effect):
        pass

    def serialize(self):
        return json.dumps({
            'gcid': self.gcid,
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
            'buff_eff': list(self.buff_eff.keys())
                           })


class GCIDManager:
    def __init__(self):
        # {gcid: GameCard, ...}
        self._cards = dict()

    def register(self, c: GameCard):
        gcid = random.randint(0, 99999999)
        while gcid in self._cards.keys():
            gcid = random.randint(0, 99999999)
        self._cards[gcid] = c
        c.gcid = gcid

    def recycle(self, gcid: int):
        self._cards.pop(gcid)

    def get_card(self, gcid: int):
        return self._cards[gcid]


class TimePoint:
    def __init__(self, tp_id: ETimePoint, sender: Effect, args):
        self.tp = tp_id
        self.sender = sender
        self.args = args

    @staticmethod
    def generate(tp_id):
        return TimePoint(tp_id, None, None)


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
        self.__batch_sending('startm', None)
        exec(self.match_config["match_init"])
        last_loser = None
        while True:
            self.game_now = Game(self.players, self.match_config["game_config"], last_loser)
            for p in self.players:
                p.init_deck(self.game_now)
            pl: tuple = self.game_now.start()
            self.wins[pl[0]] += 1
            last_loser = pl[1]
            winner: GamePlayer = self.end_check()
            if winner is not None:
                self.__batch_sending('endm', winner)
                exec(self.match_config['match_end'])
                return winner
            self.__batch_sending('endg', pl[0])
            self.__batch_sending('mbreak', None)
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

    def __batch_sending(self, op, sender, args: list = None):
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
        # 当前回合数
        self.turns = 1
        self.game_config = game_config
        self.last_loser = last_loser
        self.phase_now: EGamePhase = None
        self.winner: GamePlayer = None
        self.loser: GamePlayer = None

        # 在当前阶段所有需要检查是否满足了触发条件的效果
        self.ef_listener = list()

        self.gcid_manager = GCIDManager()

    def start(self):
        """
        双方都已准备好。开始进行游戏。
        :return: 列表，前者为获胜的玩家代表，后者为落败的玩家代表。
        """
        # sp: starting player
        # 游戏流程
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
            for p in self.players:
                p.output('startg')
        elif ph == EGamePhase.SHOW_CARD:
            self.__enter_phase(ETimePoint.PH_SHOWED_CARD)
            self.__ph_show_card()
            self.__end_phase(ETimePoint.PH_SHOWED_CARD_END)
        elif ph == EGamePhase.EXTRA_DATA:
            self.__enter_phase(ETimePoint.PH_EXTRA_DATA)
            self.__end_phase(ETimePoint.PH_EXTRA_DATA_END)
        elif ph == EGamePhase.PUT_CARD:
            self.__enter_phase(ETimePoint.PH_PUT_CARD)
            self.__end_phase(ETimePoint.PH_PUT_CARD_END)
        elif ph == EGamePhase.TAKE_CARD:
            self.__enter_phase(ETimePoint.PH_TAKE_CARD)
            self.__end_phase(ETimePoint.PH_TAKE_CARD_END)
        elif ph == EGamePhase.MULLIGAN:
            self.__enter_phase(ETimePoint.PH_MULLIGAN)
            self.__end_phase(ETimePoint.PH_MULLIGAN_END)
        elif ph == EGamePhase.PLAY_CARD:
            self.__enter_phase(ETimePoint.PH_PLAY_CARD)

    def __enter_phase(self, tp: ETimePoint):
        self.enter_time_point(TimePoint.generate(tp), False)
        self.__batch_sending('ent_ph', None, [self.phase_now.value])

    def __end_phase(self, tp):
        self.enter_time_point(TimePoint.generate(tp), False)
        self.__batch_sending('endp', None, [tp.value])

    def __ph_sp_decide(self):
        a = random.randint(1, 16)
        if a > 8:
            self.p1 = self.players[0]
            self.p2 = self.players[1]
        else:
            self.p1 = self.players[1]
            self.p2 = self.players[0]
        # 输出
        self.__batch_sending('sp_decided', self.p1)

        self.turn_player = self.p1
        self.op_player = self.p2

        self.p1.init_card_info([self.p2])
        self.p2.init_card_info([self.p1])

    def __ph_show_card(self):
        def show_one(p: GamePlayer, rank: ECardRank):
            def check_ind(ind):
                return ind in range(0, ind_max)

            p.output('req_shw_crd', [rank.value])

            card_gcid = list()
            for i in range(0, len(p.hand)):
                if p.hand[i].rank == rank:
                    card_gcid.append(p.hand[i].gcid)
            ind_max = len(p.hand)
            shown_card_index = p.input(self, check_ind, 'req_chs_tgt_f',
                                       [card_gcid, 1])

            self.show_card(p, card_gcid[shown_card_index])

        show_one(self.p1, ECardRank.TRUMP)
        show_one(self.p2, ECardRank.TRUMP)
        show_one(self.p1, ECardRank.GOOD)
        show_one(self.p2, ECardRank.GOOD)
        show_one(self.p1, ECardRank.COMMON)
        show_one(self.p2, ECardRank.COMMON)
        # todo: 删除
        self.winner = self.p1

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
            self.__batch_sending('ent_tp', None, [tp.tp.value])
        self.react()
        self.tp_stack.remove(tp)

    def enter_time_points(self):
        tts = list()
        mtts = list()
        for t in self.temp_tp_stack:
            self.tp_stack.append(t)
            tts.append(t)
            mtts.append(t.value)

        self.__batch_sending('ent_tp', None, [tp.value for tp in mtts])

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
                    op_react_list.append(ef)
                else:
                    tr_react_list.append(ef)
        if len(op_react_list) > 0 or not self.op_player.auto_skip:
            self.op_player.output('qry_rct')
            if self.op_player.input(self, check_yn, 'chs_yn'):
                ind_max = len(op_react_list)
                op_react_ef_ind = self.op_player.input(
                    self, check_eff_ind,
                    'chs_eff', [[[ef.host.serialize(), ef.description] for ef in op_react_list]])
                if op_react_ef_ind is not None:
                    # 对方响应了效果。
                    self.activate_effect(op_react_list[op_react_ef_ind])
        if len(tr_react_list) > 0 or not self.turn_player.auto_skip:
            self.turn_player.output('qry_rct')
            if self.turn_player.input(self, check_yn, 'chs_yn'):
                ind_max = len(tr_react_list)
                tr_react_ef_ind = self.turn_player.input(
                    self, check_eff_ind,
                    'chs_eff', [[[ef.host.serialize(), ef.description] for ef in tr_react_list]])
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
        self.temp_tp_stack.append(ETimePoint.PAID_COST)
        self.enter_time_points()
        if ef.succ_activate:
            ef.execute()
            self.temp_tp_stack.append(ETimePoint.SUCC_EFFECT_ACTIVATE)
        else:
            self.temp_tp_stack.append(ETimePoint.FAIL_EFFECT_ACTIVATE)
        self.enter_time_points()

    def update_ef_list(self):
        """
        手动刷新ef_list。
        :return:
        """
        pass

    def __batch_sending(self, op, sender, args: list = None):
        """
        群发消息。
        :return:
        """
        for p in self.players:
            p.output(op, args, True if sender is None else p == sender)

    def get(self, cmd: str):
        """

        :return: list
        """
        ls = cmd.split(' ')
        if ls[0] == 'gcid':
            return [self.gcid_manager.get_card(int(ls[1])).serialize()]
        return None

    # -------⬇效果函数(execute部分)⬇--------
    def activate_effect_step2(self, ef: Effect, doing_tp: ETimePoint, done_tp: ETimePoint):
        """
        适用效果。
        :param ef:
        :param doing_tp: 进行该效果时的时点，用于无效该效果。
        :param done_tp
        :return:
        """
        if doing_tp is not None:
            doing_tp = TimePoint(doing_tp, ef, None)
            self.enter_time_point(doing_tp)
        if ef is None:
            yield
            if done_tp is not None:
                done_tp = TimePoint(done_tp, None, None)
                self.enter_time_point(done_tp)
        elif ef.succ_activate:
            yield
            if done_tp is not None:
                done_tp = TimePoint(done_tp, ef, None)
                self.enter_time_point(done_tp)
        yield

    def show_card(self, p: GamePlayer, gcid, ef: Effect = None, with_tp=True):
        """
        向双方展示自己选择的卡。
        :param p: 发动效果的玩家
        :param gcid:
        :param ef: 所属效果，为None表示无源效果
        :param with_tp: 能否响应
        :return:
        """
        if with_tp:
            check_point = self.activate_effect_step2(ef, ETimePoint.SHOWING_CARD, ETimePoint.SHOWED_CARD)
            next(check_point)
            self.__batch_sending('upd_crd', p, [gcid, self.gcid_manager.get_card(gcid).serialize()])
            self.__batch_sending('shw_crd', p, [gcid])
            next(check_point)
        else:
            self.__batch_sending('upd_crd', p, [gcid, self.gcid_manager.get_card(gcid).serialize()])
            self.__batch_sending('shw_crd', p, [gcid])
