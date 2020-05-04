from utils import constants
from models.player import Player


class GameCard:
    def __init__(self, ori_o, ty):
        self.ori_owner = ori_o
        self.type = ty


class LeaderCard(GameCard):
    """
    领袖卡。
    """


class DeckCard(GameCard):
    """
    可以放在卡组中的卡（雇员/策略卡）。
    """


class Match:
    """
    一次比赛（三局两胜）。
    """
    def __init__(self, p1, p1deck, p1side, p2, p2deck, p2side, match_config):
        """

        :param p1: 玩家1
        :param p1deck: 玩家1的主卡组
        :param p1side: 玩家1的备选卡组
        :param p2:
        :param p2deck:
        :param p2side:
        :param match_config: 比赛的额外配置
        """
        self.players = [p1, p2]
        self.decks = {p1: p1deck, p2: p2deck}
        self.sides = {p1: p1side, p2: p2side}
        self.valid = self.deck_check(match_config['card_table'])
        self.match_config = match_config
        self.game_now = Game(self.players, self.decks, self.sides,
                             match_config["game_config"])

        self.wins = {p1: 0, p2: 0}

    def deck_check(self, card_table):
        """
        检查双方卡组是否有效。
        :param card_table: 比赛用卡表。
        :return:
        """
        return True

    def start(self):
        if not self.valid:
            raise Exception('invalid deck.')
        self.match_config["match_init"](self)
        while True:
            self.game_now = Game(self.players, self.decks, self.sides,
                                 self.match_config["game_config"])
            self.wins[self.game_now.start()] += 1
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


    pass


class Game:
    """
    一个单局对局。特殊规则可由领袖卡的隐藏效果引入。
    """
    def __init__(self, players, decks, sides, game_config):
        self.event_stack = list()
        pass

    def start(self):
        """
        双方都已准备好。开始进行游戏。
        :return: 获胜的玩家。
        """
        # sp: starting player
