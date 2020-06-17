from utils.constants import ECardRank, ECardType, ELocation, ETimePoint,\
    EGamePhase, EInOperation, EOutOperation
from models.player import Player
from core.io import input_from_socket, input_from_local, input_from_ai, output_2_socket,\
    output_2_local, output_2_ai, set_socket, make_output, make_input
from models.effect import Effect
from main import main_match

import random
import redis
import json

# redis键值对int/str不敏感
rds = redis.StrictRedis(db=0)


class GamePlayer:
    """
    游戏中的玩家。
    """
    def __init__(self, p: Player, deck: list, leader_card_id: int):
        def method_convert(om):
            if om == 'local':
                return input_from_local, output_2_local
            elif om == 'from_network':
                set_socket(p.upstream)
                return input_from_socket, output_2_socket
            else:
                return input_from_ai, output_2_ai
        self.player = p
        self.id = p.id
        # op_method的acceptor
        self.upstream = p.upstream
        m = method_convert(p.op_method)
        self.in_method = m[0]
        self.out_method = m[1]
        md = list()
        sd = list()
        for cid in deck:
            for i in range(deck[cid][0]):
                if int(deck[cid][3]):
                    gc = GameCard(cid, ELocation.DECK.value)
                    sd.append(gc)
                else:
                    gc = GameCard(cid, ELocation.SIDE.value)
                    md.append(gc)
        self.ori_deck = md
        self.deck = list()
        self.ori_side = sd
        self.side = sd
        # 手牌
        self.hand = md
        self.graveyard = list()
        # 除外区
        self.exiled = list()
        # 场上雇员
        self.employees = list()
        # 场上策略
        self.strategy = list()
        self.leader = GameCard(leader_card_id, ELocation.UNKNOWN)

    def input(self, *args):
        return self.in_method(self.upstream, make_input(*args))

    def output(self, *args):
        self.out_method(self.upstream, make_output(*args))


class GameCard:
    def __init__(self, cid, ori_loc, is_token=False):
        """

        :param cid:
        :param ori_loc: 初始位置。
        :param is_token:
        """
        # game card id
        self.gcid = 0
        main_match.game_now.gcid_manager.register(self)
        self.cid = cid
        self.name = rds.hget(cid, 'name')
        self.type = rds.hget(cid, 'type')
        self.subtype = rds.hget(cid, 'subtype')
        self.rank = rds.hget(cid, 'rank')
        self.src_atk = rds.hget(cid, 'atk_eff')
        self.src_def = rds.hget(cid, 'def_hp')
        self.series = rds.hget(cid, 'series')
        # 附加值。additional value
        self.add_val = 0
        # basic atk/def = source atk/def + add_val, 用于倍乘
        self.bsc_atk = 0
        self.bsc_def = 0
        self.buff_atk = 0
        self.buff_def = 0
        self.halo_atk = 0
        self.halo_def = 0
        self.is_token = is_token
        self.effects = list()
        self.location = ori_loc
        # 在对局中获得的效果。{gcid(给予该卡新效果的卡的gcid): effect, ...}
        self.buff_eff = dict()

    def register_effect(self, e: Effect):
        pass

    def serialize(self):
        return json.dumps({
            'gcid': self.gcid,
            'cid': self.cid,
            'type': self.type,
            'subtype': self.subtype,
            'rank': self.rank,
            'src_atk': self.src_atk,
            'src_def': self.src_def,
            'series': self.series,
            'add_val': self.add_val,
            'bsc_atk': self.bsc_atk,
            'bsc_def': self.bsc_def,
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
        c.gcid = gcid

    def recycle(self, gcid: int):
        self._cards.pop(gcid)

    def get_card(self, gcid: int):
        return self._cards[gcid]


class TimePoint:
    def __init__(self, tp_id, sender, location, args):
        self.value = tp_id
        self.sender = sender
        self.location = location
        self.args = args

    @staticmethod
    def generate(tp_id):
        return TimePoint(tp_id, None, None, None)


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

    def deck_check(self, card_table):
        """
        检查双方卡组是否有效。
        :param card_table: 比赛用卡表。
        :return:
        """
        for gp in self.players:
            pass
        return True

    def start(self):
        for p in self.players:
            p.output(EOutOperation.MATCH_START.value)
        exec(self.match_config["match_init"])
        last_loser = None
        while True:
            self.game_now = Game(self.players, self.match_config["game_config"], last_loser)
            pl = self.game_now.start()
            self.wins[pl[0]] += 1
            last_loser = pl[1]
            winner: GamePlayer = self.end_check()
            if winner is not None:
                for p in self.players:
                    p.output(EOutOperation.END_MATCH.value, winner.id)
                exec(self.match_config['match_end'])
                return winner
            for p in self.players:
                p.output(EOutOperation.MATCH_BREAK.value)
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

    @staticmethod
    def match_roll_deck(m):
        pass


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
        self.enter_phase(EGamePhase.GAME_START)
        for p in self.players:
            p.output(EOutOperation.GAME_START.value)

        # 游戏流程
        process = self.game_config['process']
        for ph in process:
            self.enter_phase(ph)
            if self.winner is not None:
                break
        return self.winner, self.loser

    def enter_phase(self, ph: EGamePhase):
        self.phase_now = ph
        self.update_ef_list()
        if ph == EGamePhase.GAME_START:
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_GAME_START), False)
        elif ph == EGamePhase.SP_DECIDE:
            self.__enter_phase(ETimePoint.PH_SP_DECIDE)
            self.__ph_sp_decide()
            self.__end_phase(ETimePoint.PH_SP_DECIDE_END)
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
        self.__batch_sending(EOutOperation.ENTER_PHASE.value, self.turn_player, [tp.value])

    def __end_phase(self, tp):
        self.enter_time_point(TimePoint.generate(tp), False)
        self.__batch_sending(EOutOperation.END_PHASE.value, self.turn_player, [tp.value])

    def __ph_sp_decide(self):
        a = random.randint(1, 10)
        if a > 5:
            self.p1 = self.players[0]
            self.p2 = self.players[1]
        else:
            self.p1 = self.players[1]
            self.p2 = self.players[0]
        # 输出
        self.__batch_sending(EOutOperation.SP_DECIDED.value, self.p1)

    def __ph_show_card(self):
        def show_one(p: GamePlayer, rank: ECardRank):
            p.output(EOutOperation.SHOW_A_CARD.value,
                                 [p, rank.value])

            cards_index = list()
            for i in range(0, len(p.hand)):
                if p.hand[i].rank == rank.value:
                    cards_index.append(p.hand[i])
            p.output(EOutOperation.CHOOSE_TARGET.value,
                                 [1])
            shown_card_index = p.input(EInOperation.CHOOSE_CARDS_FORCE.value,
                                       [c.serialize() for c in cards_index] + [1])
            self.__batch_sending(EOutOperation.ANNOUNCE_TARGET.value,
                                 p, [cards_index[shown_card_index].serialize()])

        show_one(self.p1, ECardRank.TRUMP)
        show_one(self.p2, ECardRank.TRUMP)
        show_one(self.p1, ECardRank.GOOD)
        show_one(self.p2, ECardRank.GOOD)
        show_one(self.p1, ECardRank.COMMON)
        show_one(self.p2, ECardRank.COMMON)
        # todo: 删除
        self.winner = self.p1

    def enter_time_point(self, tp: TimePoint, out: bool = True):
        self.tp_stack.append(tp)
        if out:
            self.__batch_sending(EOutOperation.ENTER_TIME_POINT.value, True, [tp.value])
        self.react()
        self.tp_stack.remove(tp)

    def enter_time_points(self):
        tts = list()
        mtts = list()
        for t in self.temp_tp_stack:
            self.tp_stack.append(t)
            tts.append(t)
            mtts.append(t.value)

        self.__batch_sending(EOutOperation.ENTER_TIME_POINT.value, True, mtts)

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
        self.__batch_sending(msg={'op': EOutOperation.QUERY_FOR_REACT.value})

        op_react_list = list()
        tr_react_list = list()
        for ef in self.ef_listener:
            if ef.condition():
                if ef.owner == self.p1:
                    op_react_list.append(ef)
                else:
                    tr_react_list.append(ef)

        if self.op_player.input(EInOperation.CHOOSE_YES_NO.value):
            op_react_card = self.op_player.input(EInOperation.CHOOSE_CARDS.value,
                                                 [op_react_list, 1])
            if op_react_card is not None:
                # 对方响应了效果。
                self.activate_effect(op_react_card)
        if self.turn_player.input(EInOperation.CHOOSE_YES_NO.value):
            tr_react_card = self.turn_player.input(EInOperation.CHOOSE_CARDS.value,
                                                   [tr_react_list, 1])
            if tr_react_card is not None:
                # 回合持有者响应了效果。
                self.activate_effect(tr_react_card)

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
            p.output(make_output(op, args, p == sender))
