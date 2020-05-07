from utils.constants import ECardRank, ECardType, ELocation, ETimePoint,\
    EGamePhase, EOperation
from models.player import Player
from core.input import wait_4_response_from_socket, wait_4_response,\
    wait_4_response_from_ai
import random


class GamePlayer:
    """
    游戏中的玩家。
    """
    def __init__(self, p: Player, deck: list, side: list, leader_card_id: int):
        def op_method_convert(om):
            if om == 'local':
                return wait_4_response
            elif om == 'from_network':
                return wait_4_response_from_socket
            else:
                return wait_4_response_from_ai
        self.player = p
        self.name = p.name
        # op_method的acceptor
        self.input = p.input
        self.op_method = op_method_convert(p.op_method)
        self.ori_deck = deck
        self.deck = list()
        self.ori_side = side
        self.side = side
        # 手牌
        self.hand = deck
        self.graveyard = list()
        # 除外区
        self.exiled = list()
        # 场上雇员
        self.employees = list()
        # 场上策略
        self.strategy = list()
        self.leader = leader_card_id


class GameCard:
    def __init__(self, ty):
        self.type = ty


class LeaderCard(GameCard):
    """
    领袖卡。
    """


class DeckCard(GameCard):
    """
    可以放在卡组中的卡（雇员/策略卡）。
    """


class TimePoint:
    def __init__(self, tp_id, sender, location, args):
        self.tp_id = tp_id
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
    def __init__(self, p1: Player, p1deck, p1side, p1leader_id,
                 p2: Player, p2deck, p2side, p2leader_id, match_config):
        """

        :param p1: 玩家1
        :param p1deck: 玩家1的主卡组
        :param p1side: 玩家1的备选卡组
        :param p1leader_id: 玩家1的领袖卡ID
        :param p2:
        :param p2deck:
        :param p2side:
        :param p2leader_id:
        :param match_config: 比赛的额外配置
        """
        gp1 = GamePlayer(p1, p1deck, p1side, p1leader_id)
        gp2 = GamePlayer(p2, p2deck, p2side, p2leader_id)
        self.players = [gp1, gp2]
        self.valid = self.deck_check(match_config['card_table'])
        self.match_config = match_config
        self.game_now = None

        self.wins = {p1: 0, p2: 0}

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
        if not self.valid:
            raise Exception('invalid deck.')
        self.match_config["match_init"](self)
        last_loser = None
        while True:
            self.game_now = Game(self.players, self.match_config["game_config"], last_loser)
            pl = self.game_now.start()
            self.wins[pl[0]] += 1
            last_loser = pl[1]
            winner = self.end_check()
            if winner is not None:
                self.match_config['match_end'](self)
                return winner
            self.match_config['match_break'](self)

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

    def start(self):
        """
        双方都已准备好。开始进行游戏。
        :return: 列表，前者为获胜的玩家代表，后者为落败的玩家代表。
        """
        # sp: starting player
        self.enter_phase(EGamePhase.GAME_START)
        # 游戏流程
        process = self.game_config['process']
        for ph in process:
            self.enter_phase(ph)
        return self.winner, self.loser

    def enter_phase(self, ph: EGamePhase):
        self.phase_now = ph
        self.update_ef_list()
        if ph == EGamePhase.GAME_START:
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_GAME_START))
        elif ph == EGamePhase.SP_DECIDE:
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_SP_DECIDE))
            self.__ph_sp_decide()
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_SP_DECIDE_END))
        elif ph == EGamePhase.SHOW_CARD:
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_SHOWED_CARD))
            self.__ph_show_card()
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_SHOWED_CARD_END))
        elif ph == EGamePhase.EXTRA_DATA:
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_EXTRA_DATA))
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_EXTRA_DATA_END))
        elif ph == EGamePhase.PUT_CARD:
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_PUT_CARD))
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_PUT_CARD_END))
        elif ph == EGamePhase.TAKE_CARD:
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_TAKE_CARD))
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_TAKE_CARD_END))
        elif ph == EGamePhase.MULLIGAN:
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_MULLIGAN))
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_MULLIGAN_END))
        elif ph == EGamePhase.PLAY_CARD:
            self.enter_time_point(TimePoint.generate(ETimePoint.PH_PLAY_CARD))

    def __ph_sp_decide(self):
        a = random.randint(1, 10)
        if a > 5:
            self.p1 = self.players[0]
            self.p2 = self.players[1]
        else:
            self.p1 = self.players[1]
            self.p2 = self.players[0]

    def __ph_show_card(self):
        def show_one(p: GamePlayer, rank: ECardRank):
            cards_index = list()
            for i in range(0, len(p.hand)):
                if p.hand[i] == rank:
                    cards_index.append(p.hand[i])
            msg = {'operation': EOperation.CHOOSE_CARDS_FORCE, 'alternative': cards_index,
                   'num': 1}
            shown_card_index = self.p1.op_method(self.op_player.input, msg)

        show_one(self.p1, ECardRank.TRUMP)
        show_one(self.p2, ECardRank.TRUMP)
        show_one(self.p1, ECardRank.GOOD)
        show_one(self.p2, ECardRank.GOOD)
        show_one(self.p1, ECardRank.COMMON)
        show_one(self.p2, ECardRank.COMMON)

    def enter_time_point(self, tp: TimePoint):
        self.tp_stack.append(tp)
        self.react()
        self.tp_stack.remove(tp)

    def enter_time_points(self):
        tts = list()
        for t in self.temp_tp_stack:
            self.tp_stack.append(t)
            tts.append(t)
        self.temp_tp_stack.clear()
        self.react()
        # 不需要倒序移除。
        for t in tts:
            self.tp_stack.remove(t)

    def react(self):
        """
        询问连锁。
        :return:
        """
        op_react_list = list()
        tr_react_list = list()
        for ef in self.ef_listener:
            if ef.condition():
                if ef.owner == self.p1:
                    op_react_list.append(ef)
                else:
                    tr_react_list.append(ef)
        op_msg = {'operation': EOperation.CHOOSE_CARDS, 'alternative': op_react_list,
                  'num': 1}
        tr_msg = {'operation': EOperation.CHOOSE_CARDS, 'alternative': tr_react_list,
                  'num': 1}
        op_react_card = self.op_player.op_method(self.op_player.input, op_msg)
        tr_react_card = self.turn_player.op_method(self.turn_player.input, tr_msg)
        if op_react_card is not None:
            # 对方响应了效果。
            self.activate_effect(op_react_card)
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