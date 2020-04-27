from utils import constants
from models.player import Player


class GameCard:
    pass


class LeaderCard(GameCard):
    """
    领袖卡。
    """
    pass


class DeckCard(GameCard):
    """
    可以放在卡组中的卡（雇员/策略卡）。
    """

    pass


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
        self.match_config = match_config
        self.game_now = Game(self.players, self.decks, self.sides,
                             match_config["game_config"])

        self.wins = {p1: 0, p2: 0}

    def start(self):
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
        pass

    def start(self):
        """
        双方都已准备好。开始进行游戏。
        :return: 获胜的玩家。
        """

        pass

    pass
